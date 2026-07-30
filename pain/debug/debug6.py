'''This is a build-task dependency resolver — given tasks and what they depend on, it figures out a valid run order (topological sort) and should refuse to proceed if there's a circular dependency. I wrote the recursive part fairly quickly and it worked on the one dependency graph I tried, but I never really stress-tested it:

Cycle detection — I'm using a "visited" set to avoid infinite recursion, but I have a feeling it might not actually be correctly distinguishing "currently being processed" from "already fully processed." Not sure that distinction even matters, but flagging it in case.
The final task order — I never carefully verified it comes out in an order where dependencies actually run before the tasks that need them, versus after.
Someone referenced a dependency that was never registered as its own task, and the recursion did something ugly. Didn't chase it.
The memoization cache I added to speed up repeated lookups — used a functools.lru_cache-style pattern by hand — I have a nagging feeling it's not behaving per-instance the way I expect when I have multiple resolver objects alive at once. Might be nothing.

No tests. Sorry, good luck.'''





class DependencyResolver:
      # meant to memoize resolved order per task, shared for "efficiency"

    def __init__(self):
        self.tasks = {}  # task_name -> list of dependency names
        self._cache = {}
    def add_task(self, name, depends_on=None):
        
        ''' if depends_on: # if depends_on exist
           for dep in depends_on: # in e
               if dep not in self.tasks:
                   print('invalid')
                   return'''
        '''for task, dep in self.tasks.items():
            if depends_on is task or []:
                self.tasks[name] = depends_on or []
        print('invalid')'''
        '''for dep in depends_on or []:
            if dep not in self.tasks:
                print('invalid')
                return'''

        self.tasks[name] = depends_on or []


    def _visit(self, name, visited, order):
        if name not in self.tasks:
            print('invalid')
            return
        if name in visited:
            return
        visited.add(name)

        for dep in self.tasks[name]:
            self._visit(dep, visited, order)

        order.append(name)
        self._cache[name] = order

    def resolve(self, name):
        if name in self._cache:
            return self._cache[name]

        visited = set()
        order = []
        self._visit(name, visited, order)
        return order

    def has_cycle(self, name, visited=None, stack=None):
        if visited is None:
            visited = set()
        if stack is None:
            stack = set()

        visited.add(name)
        stack.add(name)

        for dep in self.tasks[name]:
            if dep not in visited:
                if self.has_cycle(dep, visited, stack):
                    return True
            elif dep in stack:
                return True

        stack.remove(name)
        return False
    def printTasks(self):
        for task, dependances in self.tasks.items():
            print(f"Task: {task} it depends on {dependances}")
        for i, order in self._cache.items():
            print(f"task {i} : Order {order}")


def main():
    r = DependencyResolver()
    r.add_task("fetch_deps", depends_on=[])
    r.add_task("compile", depends_on=["fetch_deps"])
    r.add_task("test", depends_on=["compile"])
    r.add_task("package", depends_on=["compile", "test"])
    r.add_task("deploy", depends_on=["package"])
    r.printTasks()


    
    print("Resolve order for 'deploy':")
    print(r.resolve("deploy"))

    print("\nHas cycle (should be False)?", r.has_cycle("deploy"))

    print("\nAdding a circular dependency: A -> B -> A")
    r.add_task("A", depends_on=["B"])
    r.add_task("B", depends_on=["A"])
    print("Has cycle for A (should be True)?", r.has_cycle("A"))

    print("\nReferencing a dependency that was never added as its own task...")
    r.add_task("broken", depends_on=["ghost_task"])
    print(r.resolve("broken"))
    r.printTasks()

    print("\nCreating a second, independent resolver...")
    r2 = DependencyResolver()
    r2.add_task("standalone", depends_on=[])
    print("r2 resolve 'standalone':", r2.resolve("standalone"))
    print("Does r2 wrongly know about 'deploy' from r?", "deploy" in r2._cache)

    r.add_task("A" , depends_on=["B","C"])
    r.add_task("B" , depends_on= ["D"])
    r.add_task("C", depends_on= ["D"])
    r.add_task("D", depends_on= [])

    print(r.has_cycle("A"))

if __name__ == "__main__":
    main()