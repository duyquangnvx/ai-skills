## Bố cục tổng thể

```
src/
├── index.ts                    # entry + runtime adapter (Bun.serve / node-server / export default)
├── app.ts                      # tạo app gốc, mount tất cả feature, gắn middleware toàn cục + onError
│
├── core/                       # hạ tầng dùng chung — KHÔNG chứa nghiệp vụ
│   ├── db.ts                   # khởi tạo DB client (Drizzle/Kysely/Prisma)
│   ├── env.ts                  # validate biến môi trường bằng Zod
│   ├── error.ts                # custom error classes + onError handler
│   ├── logger.ts
│   └── types.ts                # type Bindings/Variables dùng chung cho Hono generic
│
├── middlewares/                # middleware dùng chung nhiều feature
│   ├── auth.ts
│   └── request-id.ts
│
└── features/
    ├── books/
    │   ├── book.routes.ts      # sub-app Hono — handler viết INLINE, chain method
    │   ├── book.service.ts     # nghiệp vụ thuần, không biết HTTP/Context
    │   ├── book.repository.ts  # truy cập DB
    │   ├── book.schema.ts      # Zod schema (validate + sinh type)
    │   └── book.routes.test.ts # test đặt ngay cạnh feature
    │
    ├── authors/
    │   ├── author.routes.ts
    │   ├── author.service.ts
    │   ├── author.repository.ts
    │   └── author.schema.ts
    │
    └── auth/
        ├── auth.routes.ts
        ├── auth.service.ts
        └── auth.schema.ts
```

Khác biệt với cách chia-theo-tầng (modular A ở câu trước) chỉ là **trục gom nhóm**: ở đây trục là `features/<domain>/`, mỗi domain tự chứa đủ 4 lớp của nó.

## Chi tiết từng file trong một feature

Lấy ví dụ `books`. Mình đi từ trong ra ngoài (data → logic → HTTP), vì đó là chiều phụ thuộc.

**`book.schema.ts`** — nguồn type duy nhất. Zod vừa validate runtime vừa sinh TypeScript type, tránh khai báo trùng:

```ts
import { z } from 'zod'

export const createBookSchema = z.object({
  title: z.string().min(1),
  authorId: z.string().uuid(),
})

export const bookSchema = createBookSchema.extend({
  id: z.string().uuid(),
  createdAt: z.string(),
})

export type CreateBookInput = z.infer<typeof createBookSchema>
export type Book = z.infer<typeof bookSchema>
```

**`book.repository.ts`** — chỉ nói chuyện với DB, trả về dữ liệu thô. Không có logic nghiệp vụ:

```ts
import { db } from '../../core/db'
import type { CreateBookInput, Book } from './book.schema'

export const bookRepository = {
  async findById(id: string): Promise<Book | null> {
    return db.query.books.findFirst({ where: (b, { eq }) => eq(b.id, id) }) ?? null
  },
  async create(input: CreateBookInput): Promise<Book> {
    const [row] = await db.insert(booksTable).values(input).returning()
    return row
  },
}
```

**`book.service.ts`** — nghiệp vụ thuần. Đây là chỗ đặt rule, kiểm tra điều kiện, gọi repo. **Không import `hono`, không nhận `Context`** — nhờ vậy test được như hàm bình thường và tái dùng được nếu đổi framework:

```ts
import { bookRepository } from './book.repository'
import { NotFoundError } from '../../core/error'
import type { CreateBookInput } from './book.schema'

export const bookService = {
  async getById(id: string) {
    const book = await bookRepository.findById(id)
    if (!book) throw new NotFoundError(`Book ${id} not found`)
    return book
  },
  async create(input: CreateBookInput) {
    // ví dụ rule nghiệp vụ: kiểm tra author tồn tại, chống trùng tên...
    return bookRepository.create(input)
  },
}
```

**`book.routes.ts`** — sub-app Hono. Đây là điểm mấu chốt để **giữ type inference + RPC**: handler viết **inline** và method được **chain**. Handler mỏng, chỉ điều phối: validate → gọi service → trả response:

```ts
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { bookService } from './book.service'
import { createBookSchema } from './book.schema'
import type { AppEnv } from '../../core/types'

const books = new Hono<AppEnv>()
  .get('/:id', async (c) => {
    const id = c.req.param('id')           // type được suy ra vì inline
    const book = await bookService.getById(id)
    return c.json(book)
  })
  .post('/', zValidator('json', createBookSchema), async (c) => {
    const input = c.req.valid('json')      // type lấy thẳng từ Zod schema
    const book = await bookService.create(input)
    return c.json(book, 201)
  })

export default books
export type BooksType = typeof books        // export type này nếu cần RPC client
```

Lưu ý: nếu bạn từng nghe Hono nói "đừng làm Controller" — nó nói về việc *tách hàm handler ra ngoài route* (làm mất type), **không** cấm tầng `service`. Ở đây handler vẫn inline, logic mới được đẩy sang service. Đó là cách dung hòa đúng.

## Ghép các feature lại — `app.ts` và `index.ts`

`app.ts` chỉ làm nhiệm vụ lắp ráp: middleware toàn cục, mount từng feature bằng `app.route()`, xử lý lỗi tập trung. Chain `.route()` để type chảy qua cho RPC:

```ts
// src/app.ts
import { Hono } from 'hono'
import { logger } from 'hono/logger'
import books from './features/books/book.routes'
import authors from './features/authors/author.routes'
import auth from './features/auth/auth.routes'
import { onError } from './core/error'
import type { AppEnv } from './core/types'

const app = new Hono<AppEnv>()

app.use('*', logger())

const routes = app
  .route('/books', books)
  .route('/authors', authors)
  .route('/auth', auth)

app.onError(onError)               // xử lý NotFoundError, HTTPException... tập trung

export default app
export type AppType = typeof routes   // type tổng cho RPC client dùng chung repo
```

`index.ts` tách riêng phần gắn runtime — đây là quyết định giúp app *test được* và *đổi runtime được*:

```ts
// src/index.ts — bản Node/Bun
import { serve } from '@hono/node-server'
import app from './app'

serve({ fetch: app.fetch, port: 3000 })
// Cloudflare Workers thì chỉ cần: export default app
```

## Cách scale khi nhiều feature

Khi số feature tăng, vài kỹ thuật giúp `app.ts` không phình to:

Có thể tạo file `features/index.ts` đăng ký tập trung, hoặc dùng quy ước "mỗi feature export một hàm `register(app)`" để gom việc mount. Nhưng cẩn thận: nếu bạn **cần RPC type-safe**, việc tự động hóa mount động thường làm *mất type* (TypeScript không suy được type từ vòng lặp). Khi cần RPC, vẫn nên mount thủ công và chain như trên. Đây là một trade-off thực tế, không phải lúc nào "tự động đẹp" cũng giữ được type.

Về **chia sẻ giữa các feature**: nếu `books` cần gọi nghiệp vụ của `authors`, hãy import `authorService` (lớp service), **không** import `author.routes`. Quy tắc ngầm: feature chỉ phụ thuộc *service/schema* của feature khác, không phụ thuộc *routes*. Khi quan hệ chéo trở nên rối, đó là tín hiệu nên tách một lớp `core/` hoặc `shared/` cho phần dùng chung.

## So sánh nhanh để bạn chọn đúng

Feature-based **mạnh** khi: nhiều người/team làm song song (ít đụng file của nhau), tính năng có vòng đời độc lập (dễ thêm/xóa nguyên cụm), và bạn muốn về sau tách thành package/service riêng — ranh giới đã sẵn.
