# TODO

## Cleanup
- [ ] Check for other potential duplicate functionality in the library.
- [ ] The `next_contact_pins` function was found to be triply defined (once in `utils.py`, once in `lib_func`, and potentially utilized in `autonumbering.py` logic). Ensure only one source of truth is used.
- [ ] `add_wire_labels_to_circuit` performs direct mutation of `circuit.elements`. Consider if this should be a pure function returning a new circuit or elements list to align with `PySchemaElectrical`'s functional style.

## Testing
- [ ] The library tests are currently suboptimal. Improve coverage and quality for `wire_labels.py` and `system.py` additions.
- [ ] Add regression tests to ensure PDF output remains identical after migration.

## Documentation
- [ ] Verify that all new functions have comprehensive docstrings (completed during migration).
- [ ] Add examples of using `merge_circuits` and `add_wire_labels_to_circuit` to the `examples/` directory.
