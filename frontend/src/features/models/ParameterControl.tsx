type Props = {
  id: string;
  label: string;
  value: string | number;
  type?: "number" | "text";
  disabled?: boolean;
  onChange: (value: string) => void;
  onCustom: () => void;
  onDefault: () => void;
  presets?: Array<{ label: string; value: string }>;
  defaultLabel?: string;
};

export function ParameterControl({
  id,
  label,
  value,
  type = "number",
  disabled = false,
  onChange,
  onCustom,
  onDefault,
  presets = [],
  defaultLabel = "Ollama Default",
}: Props) {
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <small>Default: {defaultLabel}</small>
      <input
        id={id}
        type={type}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
      {presets.length > 0 ? (
        <div aria-label={`${label} presets`}>
          {presets.map((preset) => (
            <button key={preset.value} type="button" disabled={disabled} onClick={() => onChange(preset.value)}>
              {preset.label}
            </button>
          ))}
        </div>
      ) : null}
      <button
        type="button"
        onClick={disabled ? onCustom : onDefault}
        aria-label={disabled ? `Personalizar ${label}` : `${label} Ollama Default`}
      >
        {disabled ? `Personalizar ${label}` : "Ollama Default"}
      </button>
    </div>
  );
}
