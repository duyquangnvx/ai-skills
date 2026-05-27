# Folder structure — default and variations

The folder shape is **flexible** — variations are fine as long as Layer 1 (communication contract) and Layer 2 (role classification) hold.

## Default shape

```
games/<gameName>/
├── <Game>Scene.ts                 # composition root: instantiate + wire
├── logic/                         # headless, no engine imports
│   ├── core/                      # gameplay mechanics + the Orchestrator
│   │   ├── <DomainNoun>.ts        # Board, Grid, Tile, Tray ...
│   │   ├── <PureFunc>.ts          # PathFinder, PlacementValidator ...
│   │   ├── rules.ts
│   │   ├── types.ts
│   │   └── <Game>Orchestrator.ts
│   ├── <metaFeature>/             # one folder per meta service
│   │   └── <Service>.ts           # Wallet, Progression, QuestTracker ...
│   └── events/
│       └── GameEventBus.ts        # only when needed; sparse use
├── view/                          # engine-side
│   ├── core/                      # gameplay views
│   │   └── <View>.ts              # BoardView, GridView, TrayView ...
│   ├── <metaFeature>/             # meta UIs mirror logic structure
│   │   └── <View>.ts              # CoinBarView, QuestPanelView ...
│   └── sequences/                 # cross-system Sequences
│       └── <Sequence>.ts          # ComboSequence, LevelClearSequence ...
├── config/
│   ├── constants.ts
│   ├── levels.ts
│   └── ...
├── assets/
│   └── manifest.ts
└── index.ts                       # export Scene + scene key
```

## Allowed variations

- Split `logic/core/` into `logic/model/` (data shapes) + `logic/logic/` (mechanics) when data is heavy.
- Split `view/` into `view/widgets/` (reusable primitives), `view/popups/`, `view/screens/`, `view/hud/`.
- Merge tiny meta features into one folder when they are trivially small.
- Different suffix taste (`*Service` vs none, `*View` vs `*Panel` vs `*Widget`) as long as it is consistent within the project.
- Different file granularity — one `BoardView.ts` versus `BoardView.ts` + `CellView.ts` + `GridLineView.ts` — based on complexity.

The test for any variation: *Does it violate Layer 1 or Layer 2?* If no, it is allowed.

## Instance lifetime

All Service / Orchestrator / View instances are **per-Scene**: created in the Scene's composition root, torn down on Scene shutdown. No singletons inside a game folder. No persistence across Scene boundaries.

Cross-game persistent data (player wallet, profile, save state) is loaded from a project-level store and **injected into the per-Scene Service** at construction. The Service is the runtime owner during the Scene's life; persistence happens above the Scene, not inside it.

```ts
// project-level store loads once
const profile = await ProfileStore.load();

// scene constructs per-Scene services with persisted values injected
const wallet = new CoinWallet(profile.coins);
const progression = new BlockBlastProgression(profile.blockBlast);

// on shutdown, scene flushes back to the store
scene.shutdown = () => ProfileStore.save({
    coins: wallet.balance,
    blockBlast: progression.snapshot(),
});
```

The Service does not know how persistence works. The composition root does.
