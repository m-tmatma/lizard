'''
Language parser for Java
'''

from .clike import CLikeReader, CLikeStates, CLikeNestingStackStates


class JavaReader(CLikeReader):
    # pylint: disable=R0903

    ext = ['java']
    language_names = ['java']

    def __init__(self, context):
        super(JavaReader, self).__init__(context)
        self.parallel_states = [
                JavaStates(context),
                CLikeNestingStackStates(context)]


class JavaStates(CLikeStates):  # pylint: disable=R0903
    def __init__(self, context):
        super(JavaStates, self).__init__(context)
        self.class_name = None

    def _state_old_c_params(self, token):
        if token == '{':
            self._state_dec_to_imp(token)

    def try_new_function(self, name):
        self.context.try_new_function(name)
        self._state = self._state_function
        if self.class_name and self.context.current_function:
            self.context.current_function.name = f"{self.class_name}::{name}"

    def _state_global(self, token):
        if token == '@':
            self._state = self._state_decorator
            return
        if token in ("class", "record", "enum"):
            self.class_name = None
            self._state = self._state_class_declaration
            return
        super(JavaStates, self)._state_global(token)

    def _state_decorator(self, _):
        self._state = self._state_post_decorator

    def _state_post_decorator(self, token):
        if token == '.':
            self._state = self._state_decorator
        else:
            self._state = self._state_global
            self._state(token)

    def _state_class_declaration(self, token):
        if token == '{':
            self._state = self._state_global
        elif token == '(':  # Record parameters
            self._state = self._state_record_parameters
        elif token[0].isalpha():
            if not self.class_name:  # Only set class name if not already set
                self.class_name = token

    def _state_record_parameters(self, token):
        if token == ')':
            self._state = self._state_class_declaration
