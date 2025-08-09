import itertools

class Component:
    """Base class for all components."""
    pass

class World:
    def __init__(self):
        self.entities = {}
        self.next_entity_id = 0
        self.systems = []
        self.entities_to_remove = set()

    def create_entity(self, *components):
        """Create a new entity and add components to it."""
        entity_id = self.next_entity_id
        self.entities[entity_id] = {}
        for component in components:
            self.add_component(entity_id, component)
        self.next_entity_id += 1
        return entity_id

    def remove_entity(self, entity_id):
        """Mark an entity for removal at the end of the frame."""
        self.entities_to_remove.add(entity_id)
        

    def cleanup_entities(self):
        """Remove all entities marked for deletion."""
        
        for entity_id in self.entities_to_remove:
            if entity_id in self.entities:
                del self.entities[entity_id]
                
        self.entities_to_remove.clear()
        

    def clear_all_entities(self):
        """Remove all entities from the world."""
        self.entities.clear()
        self.entities_to_remove.clear()

    def add_component(self, entity_id, component):
        """Add a component to an entity."""
        component_type = type(component)
        self.entities[entity_id][component_type] = component

    def remove_component(self, entity_id, component_type):
        """Remove a component from an entity."""
        if component_type in self.entities[entity_id]:
            del self.entities[entity_id][component_type]

    def get_component(self, entity_id, component_type):
        """Get a component from an entity."""
        component = self.entities.get(entity_id, {}).get(component_type)
        
        return component

    def get_entities_with_components(self, *component_types):
        """Get all entities that have a certain set of components."""
        for entity_id, components in list(self.entities.items()):
            if all(ct in components for ct in component_types):
                yield entity_id, [components[ct] for ct in component_types]

    def add_system(self, system):
        """Add a system to the world."""
        system.world = self
        self.systems.append(system)

    def process_update(self, *args, **kwargs):
        """Process all systems that are not for rendering."""
        for system in self.systems:
            if not getattr(system, 'is_render_system', False):
                system.process(*args, **kwargs)
        self.cleanup_entities()

    def process_render(self):
        """Process all rendering systems."""
        for system in self.systems:
            if getattr(system, 'is_render_system', False):
                system.process()

class System:
    """Base class for all systems."""
    def __init__(self):
        self.world = None

    def process(self, *args, **kwargs):
        raise NotImplementedError