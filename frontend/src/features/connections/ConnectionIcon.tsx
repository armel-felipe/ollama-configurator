import type { ConnectionClientId } from "./connectionCommands";
import { brandAssets } from "../../assets/brands/brandAssets";

type Props = { id: ConnectionClientId; className?: string };

export function ConnectionIcon({ id, className = "" }: Props) {
  const asset = brandAssets[id];
  return <img className={`connection-icon ${className}`} src={asset.src} alt="" aria-hidden="true" data-brand-icon={id} />;
}
