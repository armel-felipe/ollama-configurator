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
  radioPresets?: boolean;
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
  radioPresets = false,
  defaultLabel = "Ollama Default",
}: Props) {
  const accessibleLabel = id === "num_ctx" ? "Context Window" : label;
  return (
    <div className="parameter-control">
      <label htmlFor={id}>{label}</label>
      <small className="parameter-default">Default: {defaultLabel}</small>
      <input
        id={id}
        aria-label={id === "num_ctx" ? accessibleLabel : undefined}
        type={type}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
      {presets.length > 0 ? (
        radioPresets ? (
          <fieldset className="preset-group" role="radiogroup" aria-label={`${accessibleLabel} presets`} disabled={disabled}>
            <legend className="sr-only">{label}</legend>
            {presets.map((preset) => (
              <label className="preset-option" key={preset.value}>
                <input
                  type="radio"
                  name={`${id}-preset`}
                  value={preset.value}
                  checked={String(value) === preset.value}
                  disabled={disabled}
                  onChange={() => onChange(preset.value)}
                />
                <span>{preset.label}</span>
              </label>
            ))}
          </fieldset>
        ) : (
          <div className="preset-buttons" aria-label={`${accessibleLabel} presets`}>
            {presets.map((preset) => (
              <button key={preset.value} type="button" disabled={disabled} onClick={() => onChange(preset.value)}>
                {preset.label}
              </button>
            ))}
          </div>
        )
      ) : null}
      <button className="default-toggle"
        type="button"
        onClick={disabled ? onCustom : onDefault}
        aria-label={disabled ? `Personalizar ${accessibleLabel}` : `${accessibleLabel} Ollama Default`}
      >
        {disabled ? `Personalizar ${label}` : "Ollama Default"}
      </button>
    </div>
  );
}
