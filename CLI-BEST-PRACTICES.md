# CLI Application Best Practices Guide

A comprehensive guide for building robust, maintainable CLI applications with TypeScript.

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Command Structure](#2-command-structure-commanderjs)
3. [Global Options Management](#3-global-options-management)
4. [Error Handling](#4-error-handling)
5. [Input Validation](#5-input-validation-zod)
6. [Output Formatting](#6-output-formatting)
7. [Progress Indicators](#7-progress-indicators)
8. [Configuration Management](#8-configuration-management)
9. [Storage Utilities](#9-storage-utilities)
10. [Command Implementation Pattern](#10-command-implementation-pattern)
11. [Batch Operations](#11-batch-operations)
12. [Testing](#12-testing)
13. [Dependencies](#13-dependencies)
14. [TypeScript Config](#14-typescript-config)
15. [Package.json Scripts](#15-packagejson-scripts)
16. [Summary](#16-summary-key-principles)

---

## 1. Project Structure

```
src/
├── index.ts                 # Entry point, command registration
├── cli/
│   ├── commands/            # Command implementations (by feature)
│   │   ├── user/
│   │   │   ├── create.ts
│   │   │   ├── list.ts
│   │   │   └── delete.ts
│   │   └── config/
│   │       ├── show.ts
│   │       └── set.ts
│   ├── options.ts           # Global options utilities
│   └── formatters/          # Output formatting
│       ├── json.ts
│       └── table.ts
├── services/                # Business logic
│   ├── user.ts
│   ├── config.ts
│   └── storage.ts
├── models/                  # Zod schemas & types
│   ├── user.ts
│   └── config.ts
├── lib/                     # Utilities
│   ├── errors.ts
│   └── progress.ts
└── config/                  # Defaults & paths
    └── defaults.ts
tests/
├── unit/
│   ├── lib/
│   └── models/
└── integration/
    ├── cli/
    └── services/
```

### Key Principles

- **Separation of Concerns**: CLI logic in `/cli/commands`, business logic in `/services`, data definitions in `/models`
- **Feature-based Organization**: Commands grouped by domain (user, config, etc.)
- **Flat Service Layer**: Services handle business logic, delegate to storage

---

## 2. Command Structure (Commander.js)

### Entry Point

```typescript
// src/index.ts
#!/usr/bin/env node

import { Command } from 'commander';

const program = new Command();

program
  .name('mycli')
  .version('1.0.0')
  .description('My CLI application')
  .option('--json', 'Output as JSON')
  .option('-q, --quiet', 'Suppress non-essential output')
  .option('-v, --verbose', 'Verbose output');

// Group commands by feature
const userCmd = program.command('user').description('User management');

userCmd
  .command('create <name>')
  .description('Create a new user')
  .option('-e, --email <email>', 'User email')
  .option('-r, --role <role>', 'User role', 'user')
  .action(async (name, options) => {
    // Lazy load for faster startup
    const { userCreateCommand } = await import('./cli/commands/user/create.js');
    await userCreateCommand(name, options, program);
  });

userCmd
  .command('list')
  .description('List all users')
  .option('--role <role>', 'Filter by role')
  .action(async (options) => {
    const { userListCommand } = await import('./cli/commands/user/list.js');
    await userListCommand(options, program);
  });

userCmd
  .command('delete <id>')
  .description('Delete a user')
  .option('-f, --force', 'Skip confirmation')
  .action(async (id, options) => {
    const { userDeleteCommand } = await import('./cli/commands/user/delete.js');
    await userDeleteCommand(id, options, program);
  });

// Config commands
const configCmd = program.command('config').description('Configuration management');

configCmd
  .command('show')
  .description('Show current configuration')
  .action(async () => {
    const { configShowCommand } = await import('./cli/commands/config/show.js');
    await configShowCommand(program);
  });

configCmd
  .command('set <key> <value>')
  .description('Set a configuration value')
  .action(async (key, value) => {
    const { configSetCommand } = await import('./cli/commands/config/set.js');
    await configSetCommand(key, value, program);
  });

program.parse();
```

### Benefits

- **Lazy Loading**: Dynamic imports improve startup time
- **Organized Hierarchy**: Nested commands (program → subcommand → action)
- **Consistent Options**: Each command has clear, documented options

---

## 3. Global Options Management

```typescript
// src/cli/options.ts
import { Command } from 'commander';

export interface GlobalOptions {
  json?: boolean;
  quiet?: boolean;
  verbose?: boolean;
}

/**
 * Extract global options from the root program
 */
export function getGlobalOptions(program: Command): GlobalOptions {
  return program.opts() as GlobalOptions;
}

/**
 * Check if output should be suppressed
 * Note: JSON output is never suppressed even in quiet mode
 */
export function isSilent(options: GlobalOptions): boolean {
  return options.quiet === true && !options.json;
}

/**
 * Check if output should be JSON formatted
 */
export function isJSONOutput(options: GlobalOptions): boolean {
  return options.json === true;
}

/**
 * Check if verbose logging is enabled
 */
export function isVerbose(options: GlobalOptions): boolean {
  return options.verbose === true && !options.quiet;
}
```

### Usage in Commands

```typescript
const globalOpts = getGlobalOptions(program);
const silent = isSilent(globalOpts);
const jsonOutput = isJSONOutput(globalOpts);

if (jsonOutput) {
  outputJSON({ success: true, data });
} else if (!silent) {
  console.log(formatSuccess('Operation completed'));
}
```

---

## 4. Error Handling

### Custom Error Hierarchy

```typescript
// src/lib/errors.ts

/**
 * Base error class for all CLI errors
 * Each error type has a unique exit code for scripting
 */
export class CLIError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly exitCode = 1,
    public readonly cause?: unknown
  ) {
    super(message);
    this.name = 'CLIError';
  }

  /**
   * Format error for user display
   */
  format(suggestion?: string): string {
    let output = `Error [${this.code}]: ${this.message}`;
    if (suggestion) {
      output += `\n\nSuggestion: ${suggestion}`;
    }
    if (this.cause instanceof Error) {
      output += `\n\nCause: ${this.cause.message}`;
    }
    return output;
  }
}

/**
 * Configuration errors (invalid config, missing required values)
 * Exit code: 2
 */
export class ConfigError extends CLIError {
  constructor(message: string, cause?: unknown) {
    super(message, 'CONFIG_ERROR', 2, cause);
    this.name = 'ConfigError';
  }
}

/**
 * Validation errors (invalid input, schema failures)
 * Exit code: 3
 */
export class ValidationError extends CLIError {
  constructor(message: string, cause?: unknown) {
    super(message, 'VALIDATION_ERROR', 3, cause);
    this.name = 'ValidationError';
  }
}

/**
 * Storage/IO errors (file read/write failures)
 * Exit code: 4
 */
export class StorageError extends CLIError {
  constructor(message: string, cause?: unknown) {
    super(message, 'STORAGE_ERROR', 4, cause);
    this.name = 'StorageError';
  }
}

/**
 * Network errors (API failures, timeouts)
 * Exit code: 5
 */
export class NetworkError extends CLIError {
  constructor(message: string, cause?: unknown) {
    super(message, 'NETWORK_ERROR', 5, cause);
    this.name = 'NetworkError';
  }
}

/**
 * Handle error and return appropriate exit code
 */
export function handleError(error: unknown): number {
  if (error instanceof CLIError) {
    return error.exitCode;
  }
  return 1;
}

/**
 * Type guard for CLIError
 */
export function isCLIError(error: unknown): error is CLIError {
  return error instanceof CLIError;
}
```

### Exit Code Convention

| Exit Code | Error Type | Description |
|-----------|------------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | General | Unknown or unhandled error |
| 2 | ConfigError | Configuration issues |
| 3 | ValidationError | Input validation failures |
| 4 | StorageError | File I/O failures |
| 5 | NetworkError | Network/API failures |

---

## 5. Input Validation (Zod)

### Schema Definitions

```typescript
// src/models/user.ts
import { z } from 'zod';

/**
 * Full user schema - all fields required
 */
export const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(['admin', 'user', 'guest']),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type User = z.infer<typeof UserSchema>;

/**
 * Partial schema - for updates
 */
export const UserUpdateSchema = UserSchema.partial().omit({
  id: true,
  createdAt: true,
});

export type UserUpdate = z.infer<typeof UserUpdateSchema>;

/**
 * Input schema - for CLI command input
 */
export const CreateUserInputSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email format'),
  role: z.enum(['admin', 'user', 'guest']).default('user'),
});

export type CreateUserInput = z.infer<typeof CreateUserInputSchema>;
```

### Validation in Commands

```typescript
// Validate CLI input
const input = CreateUserInputSchema.safeParse({
  name,
  email: options.email,
  role: options.role,
});

if (!input.success) {
  const messages = input.error.issues.map((i) => i.message).join(', ');
  throw new ValidationError(messages);
}

// Use validated data
const user = await userService.create(input.data);
```

### Validation in Storage

```typescript
export function readJSON<T>(filePath: string, schema: z.ZodType<T>): T {
  const content = readFileSync(filePath, 'utf-8');
  const data = JSON.parse(content);
  const result = schema.safeParse(data);

  if (!result.success) {
    throw new StorageError(
      `Invalid file format: ${filePath}\n${result.error.message}`
    );
  }

  return result.data;
}
```

---

## 6. Output Formatting

### JSON Formatter

```typescript
// src/cli/formatters/json.ts

/**
 * Output data as formatted JSON
 */
export function outputJSON<T>(data: T): void {
  console.log(JSON.stringify(data, null, 2));
}

/**
 * Output error as JSON to stderr
 */
export function outputJSONError(error: {
  message: string;
  code?: string;
  exitCode?: number;
}): void {
  console.error(
    JSON.stringify(
      {
        error: true,
        message: error.message,
        code: error.code,
        exitCode: error.exitCode,
      },
      null,
      2
    )
  );
}
```

### Table Formatter

```typescript
// src/cli/formatters/table.ts
import chalk from 'chalk';

interface Column {
  key: string;
  header: string;
  width?: number;
  align?: 'left' | 'right';
  format?: (value: unknown) => string;
}

/**
 * Format data as an ASCII table
 */
export function formatTable<T extends Record<string, unknown>>(
  data: T[],
  columns: Column[]
): string {
  if (data.length === 0) {
    return chalk.dim('No data');
  }

  // Calculate column widths
  const widths = columns.map((col) => {
    const maxData = Math.max(
      ...data.map((row) => {
        const value = col.format
          ? col.format(row[col.key])
          : String(row[col.key] ?? '');
        return value.length;
      })
    );
    return col.width ?? Math.max(col.header.length, maxData);
  });

  // Header
  const header = columns
    .map((col, i) => chalk.bold(col.header.padEnd(widths[i]!)))
    .join('  ');

  // Separator
  const separator = chalk.dim(widths.map((w) => '─'.repeat(w)).join('──'));

  // Rows
  const rows = data.map((row) =>
    columns
      .map((col, i) => {
        const value = col.format
          ? col.format(row[col.key])
          : String(row[col.key] ?? '');
        return col.align === 'right'
          ? value.padStart(widths[i]!)
          : value.padEnd(widths[i]!);
      })
      .join('  ')
  );

  return [header, separator, ...rows].join('\n');
}

/**
 * Format key-value pairs
 */
export function formatKeyValue(
  data: Record<string, unknown>,
  indent = 0
): string {
  const prefix = ' '.repeat(indent);
  return Object.entries(data)
    .map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        return `${prefix}${chalk.bold(key)}:\n${formatKeyValue(
          value as Record<string, unknown>,
          indent + 2
        )}`;
      }
      return `${prefix}${chalk.bold(key)}: ${value}`;
    })
    .join('\n');
}

/**
 * Status formatters
 */
export function formatSuccess(message: string): string {
  return chalk.green('✓') + ' ' + message;
}

export function formatError(message: string): string {
  return chalk.red('✗') + ' ' + message;
}

export function formatWarning(message: string): string {
  return chalk.yellow('⚠') + ' ' + message;
}

export function formatInfo(message: string): string {
  return chalk.blue('ℹ') + ' ' + message;
}

export function formatHeader(title: string): string {
  return chalk.bold.underline(title);
}
```

### Usage Example

```typescript
// Table output
const users = await userService.getAll();
console.log(
  formatTable(users, [
    { key: 'id', header: 'ID', width: 36 },
    { key: 'name', header: 'Name', width: 20 },
    { key: 'email', header: 'Email', width: 30 },
    { key: 'role', header: 'Role', width: 10 },
  ])
);

// Key-value output
console.log(formatKeyValue({ name: 'John', email: 'john@example.com' }));

// Status messages
console.log(formatSuccess('User created successfully'));
console.log(formatError('Failed to create user'));
console.log(formatWarning('This action cannot be undone'));
```

---

## 7. Progress Indicators

```typescript
// src/lib/progress.ts
import ora, { Ora } from 'ora';
import { SingleBar, Presets } from 'cli-progress';

/**
 * Spinner for indeterminate operations
 */
export class SpinnerProgress {
  private spinner: Ora;

  constructor(text: string) {
    this.spinner = ora(text).start();
  }

  update(text: string): void {
    this.spinner.text = text;
  }

  succeed(text?: string): void {
    this.spinner.succeed(text);
  }

  fail(text?: string): void {
    this.spinner.fail(text);
  }

  warn(text?: string): void {
    this.spinner.warn(text);
  }

  info(text?: string): void {
    this.spinner.info(text);
  }

  stop(): void {
    this.spinner.stop();
  }
}

/**
 * Progress bar for determinate operations
 */
export class BarProgress {
  private bar: SingleBar;
  private current = 0;

  constructor(private total: number, format?: string) {
    this.bar = new SingleBar(
      {
        format: format ?? '{bar} {percentage}% | {value}/{total}',
        hideCursor: true,
      },
      Presets.shades_classic
    );
  }

  start(): void {
    this.bar.start(this.total, 0);
  }

  increment(delta = 1): void {
    this.current += delta;
    this.bar.update(this.current);
  }

  update(value: number): void {
    this.current = value;
    this.bar.update(value);
  }

  stop(): void {
    this.bar.stop();
  }
}

/**
 * Silent progress - no-op for quiet mode
 */
export class SilentProgress {
  update(_text: string): void {}
  succeed(_text?: string): void {}
  fail(_text?: string): void {}
  warn(_text?: string): void {}
  info(_text?: string): void {}
  stop(): void {}
  start(): void {}
  increment(_delta?: number): void {}
}

/**
 * Progress interface for polymorphism
 */
export interface Progress {
  update(text: string): void;
  succeed(text?: string): void;
  fail(text?: string): void;
  stop(): void;
}

/**
 * Create appropriate progress indicator based on silent mode
 */
export function createSpinner(text: string, silent: boolean): Progress {
  return silent ? new SilentProgress() : new SpinnerProgress(text);
}
```

### Usage Example

```typescript
const silent = isSilent(globalOpts);
const spinner = createSpinner('Processing...', silent);

try {
  spinner.update('Step 1: Validating...');
  await validate();

  spinner.update('Step 2: Processing...');
  await process();

  spinner.succeed('Completed successfully');
} catch (error) {
  spinner.fail('Processing failed');
  throw error;
}
```

---

## 8. Configuration Management

### Default Paths

```typescript
// src/config/defaults.ts
import { join } from 'path';
import { homedir } from 'os';

export const APP_NAME = 'mycli';
export const APP_DIR = join(homedir(), `.${APP_NAME}`);
export const CONFIG_PATH = join(APP_DIR, 'config.json');
export const DATA_DIR = join(APP_DIR, 'data');
export const CACHE_DIR = join(APP_DIR, 'cache');

/**
 * Get paths for a specific project
 */
export function getProjectPaths(projectName: string) {
  const projectDir = join(DATA_DIR, projectName);
  return {
    projectDir,
    configFile: join(projectDir, 'config.json'),
    dataFile: join(projectDir, 'data.json'),
  };
}
```

### Config Service (Singleton Pattern)

```typescript
// src/services/config.ts
import { z } from 'zod';
import { readJSONOrDefault, writeJSON } from './storage.js';
import { CONFIG_PATH } from '../config/defaults.js';

const ConfigSchema = z.object({
  version: z.string(),
  theme: z.enum(['light', 'dark']),
  defaultFormat: z.enum(['json', 'table']),
  editor: z.string().optional(),
  maxItems: z.number().min(1).max(1000),
});

type Config = z.infer<typeof ConfigSchema>;

const DEFAULT_CONFIG: Config = {
  version: '1.0.0',
  theme: 'dark',
  defaultFormat: 'table',
  maxItems: 100,
};

class ConfigService {
  private config: Config | null = null;

  /**
   * Load configuration from file, merge with defaults
   */
  load(): Config {
    const partial = readJSONOrDefault(
      CONFIG_PATH,
      ConfigSchema.partial(),
      {}
    );
    this.config = { ...DEFAULT_CONFIG, ...partial };
    return this.config;
  }

  /**
   * Get current configuration (lazy load)
   */
  get(): Config {
    if (!this.config) {
      return this.load();
    }
    return this.config;
  }

  /**
   * Get a specific configuration value
   */
  getValue<K extends keyof Config>(key: K): Config[K] {
    return this.get()[key];
  }

  /**
   * Update configuration
   */
  update(partial: Partial<Config>): Config {
    const current = this.get();
    this.config = { ...current, ...partial };
    writeJSON(CONFIG_PATH, this.config);
    return this.config;
  }

  /**
   * Reset to default configuration
   */
  reset(): Config {
    this.config = { ...DEFAULT_CONFIG };
    writeJSON(CONFIG_PATH, this.config);
    return this.config;
  }

  /**
   * Check if a key exists
   */
  has(key: string): boolean {
    return key in this.get();
  }
}

// Singleton instance
let instance: ConfigService | null = null;

export function getConfigService(): ConfigService {
  if (!instance) {
    instance = new ConfigService();
  }
  return instance;
}

/**
 * Reset singleton (for testing)
 */
export function resetConfigService(): void {
  instance = null;
}
```

---

## 9. Storage Utilities

```typescript
// src/services/storage.ts
import {
  readFileSync,
  writeFileSync,
  existsSync,
  mkdirSync,
  renameSync,
  unlinkSync,
  readdirSync,
} from 'fs';
import { dirname, join } from 'path';
import { tmpdir } from 'os';
import { z } from 'zod';
import { StorageError } from '../lib/errors.js';

/**
 * Read and validate JSON file
 */
export function readJSON<T>(filePath: string, schema: z.ZodType<T>): T {
  try {
    if (!existsSync(filePath)) {
      throw new StorageError(`File not found: ${filePath}`);
    }

    const content = readFileSync(filePath, 'utf-8');
    const data = JSON.parse(content);
    const result = schema.safeParse(data);

    if (!result.success) {
      throw new StorageError(
        `Invalid file format: ${filePath}\n${result.error.message}`
      );
    }

    return result.data;
  } catch (error) {
    if (error instanceof StorageError) throw error;
    throw new StorageError(`Failed to read ${filePath}`, error);
  }
}

/**
 * Read JSON file or return default value
 */
export function readJSONOrDefault<T>(
  filePath: string,
  schema: z.ZodType<T>,
  defaultValue: T
): T {
  if (!existsSync(filePath)) {
    return defaultValue;
  }

  try {
    return readJSON(filePath, schema);
  } catch {
    return defaultValue;
  }
}

/**
 * Write JSON file atomically
 * Uses temp file + rename to prevent corruption
 */
export function writeJSON<T>(filePath: string, data: T): void {
  try {
    const dir = dirname(filePath);
    ensureDir(dir);

    // Write to temp file first
    const tmpPath = join(
      tmpdir(),
      `cli-${Date.now()}-${Math.random().toString(36).slice(2)}.tmp`
    );
    writeFileSync(tmpPath, JSON.stringify(data, null, 2), 'utf-8');

    // Atomic rename
    renameSync(tmpPath, filePath);
  } catch (error) {
    throw new StorageError(`Failed to write ${filePath}`, error);
  }
}

/**
 * Read text file
 */
export function readText(filePath: string): string {
  try {
    if (!existsSync(filePath)) {
      throw new StorageError(`File not found: ${filePath}`);
    }
    return readFileSync(filePath, 'utf-8');
  } catch (error) {
    if (error instanceof StorageError) throw error;
    throw new StorageError(`Failed to read ${filePath}`, error);
  }
}

/**
 * Write text file atomically
 */
export function writeText(filePath: string, content: string): void {
  try {
    const dir = dirname(filePath);
    ensureDir(dir);

    const tmpPath = join(
      tmpdir(),
      `cli-${Date.now()}-${Math.random().toString(36).slice(2)}.tmp`
    );
    writeFileSync(tmpPath, content, 'utf-8');
    renameSync(tmpPath, filePath);
  } catch (error) {
    throw new StorageError(`Failed to write ${filePath}`, error);
  }
}

/**
 * Check if file exists
 */
export function fileExists(filePath: string): boolean {
  return existsSync(filePath);
}

/**
 * Ensure directory exists
 */
export function ensureDir(dirPath: string): void {
  if (!existsSync(dirPath)) {
    mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Delete file if exists
 */
export function deleteFile(filePath: string): void {
  if (existsSync(filePath)) {
    unlinkSync(filePath);
  }
}

/**
 * List files in directory
 */
export function listFiles(dirPath: string): string[] {
  if (!existsSync(dirPath)) {
    return [];
  }
  return readdirSync(dirPath);
}
```

---

## 10. Command Implementation Pattern

### Standard Command Structure

```typescript
// src/cli/commands/user/create.ts
import { Command } from 'commander';
import { getGlobalOptions, isSilent, isJSONOutput } from '../../options.js';
import { outputJSON, outputJSONError } from '../../formatters/json.js';
import { formatSuccess, formatError } from '../../formatters/table.js';
import { createSpinner } from '../../../lib/progress.js';
import { CreateUserInputSchema } from '../../../models/user.js';
import { ValidationError, handleError, isCLIError } from '../../../lib/errors.js';
import { getUserService } from '../../../services/user.js';

interface CreateOptions {
  email?: string;
  role?: string;
}

export async function userCreateCommand(
  name: string,
  cmdOptions: CreateOptions,
  program: Command
): Promise<void> {
  // 1. Extract global options
  const globalOpts = getGlobalOptions(program);
  const silent = isSilent(globalOpts);
  const jsonOutput = isJSONOutput(globalOpts);

  // 2. Create progress indicator
  const spinner = createSpinner('Creating user...', silent);

  try {
    // 3. Validate input
    const input = CreateUserInputSchema.safeParse({
      name,
      email: cmdOptions.email,
      role: cmdOptions.role,
    });

    if (!input.success) {
      const messages = input.error.issues.map((i) => i.message).join(', ');
      throw new ValidationError(messages);
    }

    // 4. Get service
    const userService = getUserService();

    // 5. Check for conflicts
    spinner.update('Checking for existing user...');
    const existing = await userService.findByEmail(input.data.email);
    if (existing) {
      throw new ValidationError(`User with email ${input.data.email} already exists`);
    }

    // 6. Execute business logic
    spinner.update('Creating user...');
    const user = await userService.create(input.data);

    // 7. Output success
    spinner.succeed(`User '${user.name}' created`);

    if (jsonOutput) {
      outputJSON({ success: true, user });
    } else if (!silent) {
      console.log(formatSuccess(`User created with ID: ${user.id}`));
      console.log(`  Email: ${user.email}`);
      console.log(`  Role: ${user.role}`);
    }
  } catch (error) {
    // 8. Handle errors
    spinner.fail('Failed to create user');

    const message = error instanceof Error ? error.message : String(error);
    const code = isCLIError(error) ? error.code : undefined;
    const exitCode = handleError(error);

    if (jsonOutput) {
      outputJSONError({ message, code, exitCode });
    } else if (!silent) {
      console.error(formatError(message));
    }

    process.exit(exitCode);
  }
}
```

### Command Flow Summary

1. **Extract Options**: Get global and command-specific options
2. **Create Progress**: Initialize spinner/progress based on silent mode
3. **Validate Input**: Use Zod schemas to validate CLI input
4. **Get Services**: Access business logic through service layer
5. **Check Preconditions**: Validate business rules before action
6. **Execute Logic**: Perform the main operation
7. **Output Success**: Respect output mode (JSON/table/silent)
8. **Handle Errors**: Consistent error formatting and exit codes

---

## 11. Batch Operations

### Batch Processing Pattern

```typescript
// src/cli/commands/user/batch-create.ts
import { Command } from 'commander';
import { getGlobalOptions, isSilent, isJSONOutput } from '../../options.js';
import { outputJSON } from '../../formatters/json.js';
import { formatSuccess, formatError, formatWarning } from '../../formatters/table.js';
import { BarProgress, SilentProgress } from '../../../lib/progress.js';
import { getUserService } from '../../../services/user.js';

interface BatchResult {
  item: string;
  success: boolean;
  error?: string;
}

export async function userBatchCreateCommand(
  filePath: string,
  program: Command
): Promise<void> {
  const globalOpts = getGlobalOptions(program);
  const silent = isSilent(globalOpts);
  const jsonOutput = isJSONOutput(globalOpts);

  try {
    // 1. Load input data
    const users = loadUsersFromFile(filePath);

    // 2. Initialize progress
    const progress = silent
      ? new SilentProgress()
      : new BarProgress(users.length);
    progress.start();

    // 3. Process with error isolation
    const results: BatchResult[] = [];
    const userService = getUserService();

    for (const userData of users) {
      try {
        await userService.create(userData);
        results.push({ item: userData.name, success: true });
      } catch (error) {
        results.push({
          item: userData.name,
          success: false,
          error: error instanceof Error ? error.message : String(error),
        });
      }
      progress.increment();
    }

    progress.stop();

    // 4. Summarize results
    const successCount = results.filter((r) => r.success).length;
    const failCount = results.filter((r) => !r.success).length;

    if (jsonOutput) {
      outputJSON({
        success: failCount === 0,
        total: users.length,
        succeeded: successCount,
        failed: failCount,
        results,
      });
    } else if (!silent) {
      console.log('');
      console.log(formatSuccess(`Created: ${successCount}`));
      if (failCount > 0) {
        console.log(formatError(`Failed: ${failCount}`));
        results
          .filter((r) => !r.success)
          .forEach((r) => {
            console.log(formatWarning(`  ${r.item}: ${r.error}`));
          });
      }
    }

    // 5. Exit with appropriate code
    if (failCount > 0) {
      process.exit(1);
    }
  } catch (error) {
    // Handle fatal errors (file not found, etc.)
    if (jsonOutput) {
      outputJSON({
        success: false,
        error: error instanceof Error ? error.message : String(error),
      });
    } else {
      console.error(formatError(error instanceof Error ? error.message : String(error)));
    }
    process.exit(1);
  }
}
```

### Key Batch Patterns

- **Error Isolation**: Failures don't stop the entire batch
- **Progress Tracking**: Show progress for long-running operations
- **Result Aggregation**: Collect and summarize all results
- **Partial Success**: Exit code indicates if any failures occurred

---

## 12. Testing

### Test Structure

```
tests/
├── unit/
│   ├── lib/
│   │   ├── errors.test.ts
│   │   └── progress.test.ts
│   └── models/
│       └── user.test.ts
└── integration/
    ├── cli/
    │   ├── formatters.test.ts
    │   └── options.test.ts
    └── services/
        ├── config.test.ts
        └── storage.test.ts
```

### Unit Test Example

```typescript
// tests/unit/lib/errors.test.ts
import { describe, it, expect } from 'vitest';
import {
  CLIError,
  ConfigError,
  ValidationError,
  handleError,
} from '../../../src/lib/errors.js';

describe('CLI Errors', () => {
  describe('CLIError', () => {
    it('should create error with code and exit code', () => {
      const error = new CLIError('Test error', 'TEST_ERROR', 10);

      expect(error.message).toBe('Test error');
      expect(error.code).toBe('TEST_ERROR');
      expect(error.exitCode).toBe(10);
    });

    it('should format error message', () => {
      const error = new CLIError('Test error', 'TEST_ERROR');
      const formatted = error.format('Try again');

      expect(formatted).toContain('Error [TEST_ERROR]: Test error');
      expect(formatted).toContain('Suggestion: Try again');
    });

    it('should include cause in format', () => {
      const cause = new Error('Original error');
      const error = new CLIError('Wrapped error', 'WRAP', 1, cause);
      const formatted = error.format();

      expect(formatted).toContain('Cause: Original error');
    });
  });

  describe('ConfigError', () => {
    it('should have exit code 2', () => {
      const error = new ConfigError('Config missing');
      expect(error.exitCode).toBe(2);
      expect(error.code).toBe('CONFIG_ERROR');
    });
  });

  describe('handleError', () => {
    it('should return exit code from CLIError', () => {
      const error = new ValidationError('Invalid input');
      expect(handleError(error)).toBe(3);
    });

    it('should return 1 for unknown errors', () => {
      expect(handleError(new Error('Unknown'))).toBe(1);
      expect(handleError('string error')).toBe(1);
    });
  });
});
```

### Integration Test Example

```typescript
// tests/integration/cli/formatters.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { outputJSON, outputJSONError } from '../../../src/cli/formatters/json.js';
import { formatTable, formatSuccess } from '../../../src/cli/formatters/table.js';

describe('CLI Formatters', () => {
  describe('JSON Formatter', () => {
    let consoleSpy: ReturnType<typeof vi.spyOn>;

    beforeEach(() => {
      consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    });

    afterEach(() => {
      consoleSpy.mockRestore();
    });

    it('should output formatted JSON', () => {
      const data = { name: 'test', count: 42 };
      outputJSON(data);

      expect(consoleSpy).toHaveBeenCalledWith(
        JSON.stringify(data, null, 2)
      );
    });

    it('should output nested objects', () => {
      const data = { user: { name: 'John', roles: ['admin'] } };
      outputJSON(data);

      const output = consoleSpy.mock.calls[0]?.[0];
      expect(JSON.parse(output as string)).toEqual(data);
    });
  });

  describe('Table Formatter', () => {
    it('should format data as table', () => {
      const data = [
        { id: '1', name: 'Alice' },
        { id: '2', name: 'Bob' },
      ];

      const result = formatTable(data, [
        { key: 'id', header: 'ID' },
        { key: 'name', header: 'Name' },
      ]);

      expect(result).toContain('ID');
      expect(result).toContain('Name');
      expect(result).toContain('Alice');
      expect(result).toContain('Bob');
    });

    it('should return "No data" for empty array', () => {
      const result = formatTable([], [{ key: 'id', header: 'ID' }]);
      expect(result).toContain('No data');
    });
  });
});
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    testTimeout: 10000,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/index.ts'],
    },
  },
});
```

---

## 13. Dependencies

### Production Dependencies

```json
{
  "dependencies": {
    "commander": "^14.0.0",
    "chalk": "^5.3.0",
    "ora": "^8.0.0",
    "cli-progress": "^3.12.0",
    "zod": "^3.23.0",
    "dotenv": "^16.0.0"
  }
}
```

| Package | Purpose |
|---------|---------|
| commander | CLI framework (commands, options, arguments) |
| chalk | Terminal colors and styles |
| ora | Spinner/loading indicators |
| cli-progress | Determinate progress bars |
| zod | Runtime schema validation |
| dotenv | Environment variable loading |

### Development Dependencies

```json
{
  "devDependencies": {
    "typescript": "^5.5.0",
    "vitest": "^2.0.0",
    "@types/node": "^22.0.0",
    "@types/cli-progress": "^3.11.0",
    "eslint": "^9.0.0",
    "@eslint/js": "^9.0.0",
    "typescript-eslint": "^8.0.0",
    "eslint-config-prettier": "^10.0.0",
    "prettier": "^3.0.0"
  }
}
```

---

## 14. TypeScript Config

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "verbatimModuleSyntax": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### Key Options Explained

| Option | Purpose |
|--------|---------|
| `strict` | Enable all strict type-checking options |
| `noUncheckedIndexedAccess` | Add `undefined` to index signatures |
| `noImplicitReturns` | Ensure all code paths return a value |
| `verbatimModuleSyntax` | Enforce explicit type imports |
| `moduleResolution: NodeNext` | Support ESM with `.js` extensions |

---

## 15. Package.json Scripts

```json
{
  "name": "mycli",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "mycli": "./dist/index.js"
  },
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsc --watch",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src",
    "lint:fix": "eslint src --fix",
    "format": "prettier --write \"src/**/*.ts\"",
    "format:check": "prettier --check \"src/**/*.ts\"",
    "typecheck": "tsc --noEmit",
    "clean": "rm -rf dist",
    "prepublishOnly": "npm run build"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## 16. Summary: Key Principles

| Principle | Implementation |
|-----------|----------------|
| **Output Modes** | `--json` for automation, `--quiet` for scripts, default for humans |
| **Exit Codes** | Unique codes per error type for scripting integration |
| **Validation** | Zod schemas at all I/O boundaries |
| **Atomic Writes** | Write to temp file, then rename to prevent corruption |
| **Lazy Loading** | Dynamic imports for faster startup |
| **Singleton Services** | With reset functions for testing |
| **Progress Feedback** | Spinners/bars with silent mode support |
| **Separation** | CLI logic ≠ Business logic ≠ Storage |
| **Error Isolation** | Batch operations continue on individual failures |
| **Type Safety** | Strict TypeScript, generics, infer types from schemas |

### Quick Start Checklist

- [ ] Set up project structure with separated concerns
- [ ] Configure TypeScript with strict mode
- [ ] Set up ESLint and Prettier
- [ ] Create custom error classes with exit codes
- [ ] Implement global options (--json, --quiet, --verbose)
- [ ] Create JSON and table formatters
- [ ] Implement progress indicators with silent mode
- [ ] Set up configuration service with singleton pattern
- [ ] Create atomic storage utilities
- [ ] Write unit and integration tests
- [ ] Document commands with clear descriptions

---

## License

MIT
