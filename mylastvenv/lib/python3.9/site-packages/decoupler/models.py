from django.db import models


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        adaptee = kwargs.pop('adaptee')

        if len(bases) == 1 and bases[0] == models.Model:
            return super().__new__(cls, name, bases, attrs, **kwargs)

        attrs['_obj'] = None
        attrs['__init__'] = cls.init(adaptee)
        attrs['__getattr__'] = cls.getattr
        return super().__new__(cls, name, bases, attrs, **kwargs)

    @classmethod
    def init(cls, adaptee):
        def init(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)
            if not self._state.adding:
                if 'id' in kwargs:
                    del kwargs['id']
                else:
                    args = args[1:]

            self._obj = adaptee(*args, **kwargs)

        return init

    def getattr(self, attr):
        obj = self._obj
        return getattr(obj, attr)


class Model(models.Model, metaclass=ModelBase, adaptee=None):
    class Meta:
        abstract = True
