<!-- Only loads when .tsx files are read — free to keep in non-React projects. -->

# TypeScript — React

- Derive, don't sync: values computable from props/state are computed during render — never `useEffect` + `setState` to mirror other state.
- Every `useEffect` has a correct dependency array and, when it subscribes or allocates, a cleanup. Don't suppress `exhaustive-deps` — restructure the code instead.
- In server-component frameworks (Next.js App Router): components stay server components by default; add `"use client"` only at the interactive leaves.
