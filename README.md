This is the GLSL parser copied from: https://www.khronos.org/files/opengles_shading_language.pdf

Goal of this project is to allow ast-level transformations on GLSL ES -code, for example on WEBGL code.

The `generate_parser.py` creates the `glsl_es.json` from `glsl_es.gr`, producing a canonical `LR(1)` parser. The grammar contains a shift/reduce -conflict (the dangling else), which is solved by defaulting to shift.

Parser is supposed to be annotated with function names and mappings. You'll get yourself a GLSL parser by filling few structures and reimplementing the `tokenizer.py` and `parser.py` in your language. I'm not sure about all the necessary constructs so the annotations are incomplete.

The macroprocessing is insufficient here. When the annotations are completed, it might still function as long as you don't use the preprocessor macros in your code.

The `lrkit` required by `generate_parser.py` can be found from: http://github.com/cheery/lrkit
