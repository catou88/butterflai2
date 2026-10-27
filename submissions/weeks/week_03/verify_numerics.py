"""Independently check the submitted notebook's 2D objective and gradients.

Run from any directory:
    python verify_numerics.py --output numerical_verification.json

Only selected constants and function definitions are loaded from the sibling
notebook. Its data preparation, model fitting, plotting, and checkpoint writes
are not executed. No model implementation is copied into this verifier.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import trapezoid
from scipy.special import expit


FUNCTIONS = {
    "time_shape", "softplus", "width_constant", "make_intensity",
    "shared_parameters", "drift", "belt_field", "intensity_2d",
    "integrate_2d", "log_likelihood_2d", "unpack_shared",
    "trapezoid_weights", "field_derivatives", "pooled_shape_value_gradient",
    "_make_amplitude_width", "width_latitude",
}
CONSTANTS = {
    "S_A", "S_B", "N_MESH", "S_MESH", "N_S_2D", "N_LAM_2D",
    "S_2D", "LAM_2D", "MESH_2D", "B_CRIT", "ALPHA", "MU_REF",
    "LAM_MAX", "SEED",
}


def assigned_names(node):
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        return set().union(*(assigned_names(value) for value in node.elts))
    return set()


def load_functions(notebook_path):
    notebook = json.loads(notebook_path.read_text())
    namespace = {"np": np, "trapezoid": trapezoid, "expit": expit}
    loaded = set()
    code_cells = []
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        code_cells.append(source)
        for node in ast.parse(source).body:
            keep = isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS
            if isinstance(node, ast.Assign):
                names = set().union(*(assigned_names(value) for value in node.targets))
                keep = bool(names) and names <= CONSTANTS
            if keep:
                exec(compile(ast.Module(body=[node], type_ignores=[]),
                             f"notebook-cell-{index}", "exec"), namespace)
                if isinstance(node, ast.FunctionDef):
                    loaded.add(node.name)
    missing = FUNCTIONS - loaded
    if missing:
        raise RuntimeError(f"Notebook functions missing: {sorted(missing)}")
    # These are the attributes attached by the notebook immediately after its
    # rule definition; setting them does not reproduce the rule implementation.
    namespace["width_latitude"].width_kind = "latitude"
    namespace["source_code_sha256"] = hashlib.sha256(
        "\n".join(code_cells).encode()).hexdigest()
    return namespace


def centred_difference(function, parameters, step=1e-5):
    derivative = []
    for index in range(len(parameters)):
        plus, minus = parameters.copy(), parameters.copy()
        plus[index] += step
        minus[index] -= step
        derivative.append((function(plus) - function(minus)) / (2 * step))
    return np.asarray(derivative)


def verify(notebook_path):
    model = load_functions(notebook_path)
    mesh = model["MESH_2D"]
    s_nodes, latitude_nodes = mesh
    if (len(s_nodes), len(latitude_nodes)) != (201, 241):
        raise AssertionError("The mandated fitting mesh changed")
    rng = np.random.default_rng(919)
    events = {
        name: (rng.uniform(0, 50, 123), rng.uniform(-5.9, 10.9, 123))
        for name in ("A", "B")
    }
    amplitudes, labels, c = {"A": 5000.0, "B": 45000.0}, list(events), 0.0002
    amplitude_rule = model["_make_amplitude_width"](20000.0)
    cases = [
        ("constant", model["width_constant"], []),
        ("amplitude-positive", amplitude_rule, [0.3]),
        ("amplitude-negative", amplitude_rule, [-0.3]),
        ("latitude-positive", model["width_latitude"], [0.12]),
        ("latitude-negative", model["width_latitude"], [-0.08]),
    ]
    results = []
    for name, rule, extra in cases:
        q = np.r_[np.log([6.7, 0.82, 14.6, 7.2, 5.5]), extra]
        n_width = 1 + len(extra)

        def objective(parameters):
            return model["pooled_shape_value_gradient"](
                parameters, events, labels, amplitudes, c, rule, n_width, mesh)[0]

        value, gradient = model["pooled_shape_value_gradient"](
            q, events, labels, amplitudes, c, rule, n_width, mesh)
        shared = model["unpack_shared"](q, rule, c, n_width)
        generic = -sum(model["log_likelihood_2d"](
            *events[label], model["make_intensity"](amplitudes[label], shared), mesh)
            for label in labels)
        numeric = centred_difference(objective, q)
        scaled_error = np.abs(gradient - numeric) / np.maximum(1, np.abs(numeric))

        def profiled(parameters):
            unit = model["unpack_shared"](parameters, rule, 1.0, n_width)
            expected = sum(model["integrate_2d"](
                model["make_intensity"](amplitudes[label], unit)(
                    latitude_nodes[:, None], s_nodes[None, :]), mesh)
                for label in labels)
            scale = sum(len(events[label][0]) for label in labels) / expected
            return model["pooled_shape_value_gradient"](
                parameters, events, labels, amplitudes, scale, rule, n_width, mesh)

        _, envelope_gradient = profiled(q)
        profile_numeric = centred_difference(lambda parameters: profiled(parameters)[0], q)
        envelope_error = np.abs(envelope_gradient - profile_numeric) / np.maximum(
            1, np.abs(profile_numeric))
        if abs(value - generic) >= 1e-7:
            raise AssertionError(f"{name}: objective differs from generic 2D likelihood")
        if scaled_error.max() >= 1e-5 or envelope_error.max() >= 1e-5:
            raise AssertionError(f"{name}: derivative disagrees with finite differences")
        results.append(dict(
            width_rule=name, objective_absolute_difference_nats=float(abs(value-generic)),
            maximum_gradient_absolute_error=float(np.max(np.abs(gradient-numeric))),
            maximum_gradient_scaled_error=float(scaled_error.max()),
            profile_c_envelope_maximum_scaled_error=float(envelope_error.max()),
            gradient=gradient.tolist(), finite_difference=numeric.tolist(),
        ))

    latitude, time = events["A"]
    domain_area = float((s_nodes[-1]-s_nodes[0]) *
                        (latitude_nodes[-1]-latitude_nodes[0]))
    constant_errors = []
    for intensity in (0.1, 0.5, 2.0):
        value = model["log_likelihood_2d"](
            latitude, time,
            lambda la, s: np.full(np.broadcast(la, s).shape, intensity), mesh)
        analytic = len(latitude)*np.log(intensity) - intensity*domain_area
        constant_errors.append(float(abs(value-analytic)))
    if max(constant_errors) >= 1e-9:
        raise AssertionError("Constant-intensity likelihood failed its analytic check")
    return dict(
        status="PASS", source_code_sha256=model["source_code_sha256"],
        seed=919, artificial_events=246, artificial_units=2,
        mesh_nodes=[len(s_nodes), len(latitude_nodes)],
        finite_difference_step=1e-5, scaled_error_tolerance=1e-5,
        scaled_error_definition="abs(gradient - finite_difference) / max(1, abs(finite_difference))",
        maximum_constant_intensity_likelihood_error_nats=max(constant_errors),
        cases=results,
        scope="Selected interior parameter cases, not a proof over the entire parameter domain; no fitting or forecasting benchmark.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(Path(__file__).with_name("03_latent_belt.ipynb"))
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
