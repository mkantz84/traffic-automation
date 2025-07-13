import React, { useState } from "react";
import type { SimulationFormData } from "../../types";
import "./SimulationForm.css";

type Props = {
  onSubmit: (data: SimulationFormData) => void;
  disabled?: boolean;
};

const onlyNumbersAndCommas = (value: string) => value.replace(/[^0-9.,-]/g, "");
const onlyNumbersAndDot = (value: string) => value.replace(/[^0-9.-]/g, "");

const SimulationForm: React.FC<Props> = ({ onSubmit, disabled }) => {
  const [form, setForm] = useState<SimulationFormData>({
    accel: "",
    tau: "",
    startupDelay: "",
    expected_I2: "",
    expected_I3: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    let newValue = value;
    if (["accel", "tau", "startupDelay"].includes(name)) {
      newValue = onlyNumbersAndCommas(value);
    } else if (["expected_I2", "expected_I3"].includes(name)) {
      newValue = onlyNumbersAndDot(value);
    }
    setForm({ ...form, [name]: newValue });
  };

  const allFieldsSet = Object.values(form).every((v) => v.trim() !== "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form className="simulation-form" onSubmit={handleSubmit}>
      <label>
        Accel (comma-separated):
        <input
          name="accel"
          value={form.accel}
          onChange={handleChange}
          disabled={disabled}
          inputMode="decimal"
          pattern="[0-9.,-]*"
        />
      </label>
      <br />
      <label>
        Tau (comma-separated):
        <input
          name="tau"
          value={form.tau}
          onChange={handleChange}
          disabled={disabled}
          inputMode="decimal"
          pattern="[0-9.,-]*"
        />
      </label>
      <br />
      <label>
        Startup Delay (comma-separated):
        <input
          name="startupDelay"
          value={form.startupDelay}
          onChange={handleChange}
          disabled={disabled}
          inputMode="decimal"
          pattern="[0-9.,-]*"
        />
      </label>
      <br />
      <label>
        Expected Delay I2:
        <input
          name="expected_I2"
          value={form.expected_I2}
          onChange={handleChange}
          disabled={disabled}
          inputMode="decimal"
          pattern="[0-9.\-]*"
        />
      </label>
      <br />
      <label>
        Expected Delay I3:
        <input
          name="expected_I3"
          value={form.expected_I3}
          onChange={handleChange}
          disabled={disabled}
          inputMode="decimal"
          pattern="[0-9.\-]*"
        />
      </label>
      <br />
      <button type="submit" disabled={disabled || !allFieldsSet}>
        Run Simulations
      </button>
    </form>
  );
};

export default SimulationForm;
