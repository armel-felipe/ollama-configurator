import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const frontend = resolve(root, "frontend");
const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const skipInstall = args.includes("--skip-install");
const skipBuild = args.includes("--skip-build");
const outputIndex = args.indexOf("--output");
const output = resolve(root, outputIndex >= 0 ? args[outputIndex + 1] : "dist/frontend");
const packageJson = JSON.parse(await readFile(resolve(frontend, "package.json"), "utf8"));
const manifest = {
  artifact: "OllamaConfiguratorFrontend",
  version: process.env.OLLAMA_CONFIGURATOR_VERSION ?? packageJson.version,
  source: "frontend/dist",
  bind_host: "127.0.0.1",
};

async function copyClean(source, destination) {
  await mkdir(destination, { recursive: true });
  for (const entry of await readdir(source, { withFileTypes: true })) {
    if (entry.name.startsWith("._") || entry.name === ".DS_Store") continue;
    const sourcePath = join(source, entry.name);
    const destinationPath = join(destination, entry.name);
    if (entry.isDirectory()) {
      await copyClean(sourcePath, destinationPath);
    } else {
      await cp(sourcePath, destinationPath);
    }
  }
}

if (!dryRun) {
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  if (!skipInstall) {
    const install = spawnSync(npm, ["ci"], { cwd: frontend, stdio: "inherit" });
    if (install.status !== 0) process.exit(install.status ?? 1);
  }
  if (!skipBuild) {
    const build = spawnSync(npm, ["run", "build"], { cwd: frontend, stdio: "inherit" });
    if (build.status !== 0) process.exit(build.status ?? 1);
  }
  if (!existsSync(resolve(frontend, "dist"))) {
    console.error("Frontend build output not found: frontend/dist");
    process.exit(1);
  }
  await rm(output, { recursive: true, force: true });
  await mkdir(output, { recursive: true });
  await copyClean(resolve(frontend, "dist"), output);
  await writeFile(resolve(output, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
}

console.log(JSON.stringify(manifest));
