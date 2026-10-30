"""Hook for the Hailo AI HAT+ person detector.

The rule-based hotspot finder in thermal.py is the baseline. When a thermal
person-detection model is compiled to a .hef, run it here and keep both, so
you can report "model vs threshold" in the metrics table.

Sketch (hailo-apps / hailort Python API):

    from hailo_platform import HEF, VDevice, InferVStreams, ...
    hef = HEF("models/thermal_person.hef")
    ...

Inputs: 8-bit AGC'd Lepton frame upscaled to the model size.
Outputs: boxes in pixel coords -> feed the box centres to georef.pixel_to_ground.
"""


def detect(frame_u8):
    raise NotImplementedError("compile a model to .hef and wire it in here")
