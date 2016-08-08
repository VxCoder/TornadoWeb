# -*- coding: utf-8 -*-


class SubclassMetaclass(type):
    
    _super_class = []
    
    def __new__(cls, name, bases, attrs):
        
        subclass = r'.'.join([attrs[r'__module__'], attrs[r'__qualname__']])
        
        for base in bases:
            
            if(base in cls._super_class):
                
                base._subclasses.append(subclass)
                
            else:
                
                cls._super_class.append(base)
                
                setattr(base, r'_subclasses', [subclass])
        
        return type.__new__(cls, name, bases, attrs)

