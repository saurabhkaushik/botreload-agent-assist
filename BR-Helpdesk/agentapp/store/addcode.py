

class app_namespace_manager(object):
    self.namespace = 
    def getNamespace (self): 
        
    def setNamespace(self, namespace='default'):
        # Save the current namespace.
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(namespace)
            print ('Setting namespace : ' + namespace)
        finally:
            # Restore the saved namespace.
            namespace_manager.set_namespace(previous_namespace)