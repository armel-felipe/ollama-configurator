import { ollamaBrandAsset } from "../../assets/brands/brandAssets";

export function OllamaLogo() {
  return <img className="ollama-logo" src={ollamaBrandAsset.src} alt="" aria-hidden="true" data-ollama-brand />;
}
