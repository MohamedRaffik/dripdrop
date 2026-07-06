import { ActionIcon, Textarea, type ActionIconProps, type TextareaProps } from "@mantine/core";
import { useUncontrolled } from "@mantine/hooks";
import { MdVisibility, MdVisibilityOff } from "react-icons/md";

export type SensitiveTextareaProps = TextareaProps & {
  visible?: boolean;
  defaultVisible?: boolean;
  onVisibilityChange?: (visible: boolean) => void;
  visibilityToggleButtonProps?: ActionIconProps & React.ComponentPropsWithoutRef<"button">;
};

const SensitiveTextarea = ({
  visible,
  defaultVisible,
  onVisibilityChange,
  visibilityToggleButtonProps,
  rightSection,
  rightSectionPointerEvents,
  disabled,
  radius,
  styles,
  ...textareaProps
}: SensitiveTextareaProps) => {
  const [revealed, setRevealed] = useUncontrolled({
    value: visible,
    defaultValue: defaultVisible,
    finalValue: false,
    onChange: onVisibilityChange,
  });

  const toggleVisibility = () => setRevealed(!revealed);
  const maskStyles = !revealed ? ({ WebkitTextSecurity: "disc" } as const) : {};

  const visibilityToggleButton = (
    <ActionIcon
      variant="subtle"
      color="gray"
      disabled={disabled}
      radius={radius}
      aria-pressed={revealed}
      tabIndex={-1}
      {...visibilityToggleButtonProps}
      onTouchEnd={(event) => {
        event.preventDefault();
        visibilityToggleButtonProps?.onTouchEnd?.(event);
        toggleVisibility();
      }}
      onMouseDown={(event) => {
        event.preventDefault();
        visibilityToggleButtonProps?.onMouseDown?.(event);
        toggleVisibility();
      }}
      onKeyDown={(event) => {
        visibilityToggleButtonProps?.onKeyDown?.(event);
        if (event.key === " ") {
          event.preventDefault();
          toggleVisibility();
        }
      }}
    >
      {revealed ? <MdVisibilityOff size={16} /> : <MdVisibility size={16} />}
    </ActionIcon>
  );

  return (
    <Textarea
      {...textareaProps}
      disabled={disabled}
      radius={radius}
      rightSection={rightSection ?? visibilityToggleButton}
      rightSectionPointerEvents={rightSectionPointerEvents || "all"}
      styles={
        typeof styles === "function"
          ? (theme, props, ctx) => {
              const resolved = styles(theme, props, ctx);
              return {
                ...resolved,
                input: { ...resolved?.input, ...maskStyles },
              };
            }
          : {
              ...styles,
              input: { ...styles?.input, ...maskStyles },
            }
      }
    />
  );
};

export default SensitiveTextarea;
