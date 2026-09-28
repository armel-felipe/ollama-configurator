type Props = {
  id: string;
  label: string;
  value: string | number;
  type?: "number" | "text";
  disabled?: boolean;
  onChange: (value: string) => void;
  onCustom: () => void;
  onDefault: () => void;
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
}: Props) {
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
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
