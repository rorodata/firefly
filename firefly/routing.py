from werkzeug.routing import Rule
import uuid

# Mapping from Python types to werkzeug converter names
DEFAULT_TYPE_CONVERTERS = {
    None: "default",
    str: "string",
    int: "int",
    float: "float",
    uuid.UUID: "uuid"
}

class FireflyRule(Rule):
    """FireflyRule represents one URL pattern in the Firefly application.

    FireflyRule extends the default Rule class from Flask/werkzeug
    and uses the function signature to decide the converters.

    For example, consider the following route in Flask.

        @app.route("/posts/<int:post_id>")
        def show_post(post_id):
            ...

    In Firefly, it is written as:

        @app.route("/posts/<post_id>")
        def show_post(post_id: int):
            ...

    This makes Firefly consistent in dealing with function arguments
    coming from URL and from POST data.
    """
    def __init__(self, string, *, view_function=None, **kwargs):
        super().__init__(string, **kwargs)
        self.view_function = view_function

    def compile(self):
        super().compile()
        if self.view_function:
            self.bind_view_function()

    def bind_view_function(self):
        sig = self.view_function.sig

        # Update the converters based on the type annotaions
        for arg in self.arguments:
            if arg in sig.parameters:
                argtype = sig.parameters[arg].annotation
                self._converters[arg] = self._get_type_converter(arg, argtype)

        self.view_function.set_route_params(self.arguments)

    def _get_type_converter(self, arg, type):
        """Returns the appropriate converter for the specified type annotation.
        """
        if type not in DEFAULT_TYPE_CONVERTERS:
            raise LookupError("No converter found for %r" % type)
        converter_name = DEFAULT_TYPE_CONVERTERS[type]
        print("_get_type_converter", type, converter_name)
        c_args = ()
        c_kwargs = {}
        return self.get_converter(arg, converter_name, c_args, c_kwargs)
