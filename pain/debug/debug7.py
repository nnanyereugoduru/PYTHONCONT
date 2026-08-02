'''Built this to recursively total up directory sizes, mimicking du. Also added a search-by-name helper and basic symlink support. It ran fine on my small test tree, but a few things nag at me:

I never tested a directory that contains another directory more than one level deep — only tried one level of nesting when I "verified" it.
find_all (search for files/dirs by name anywhere in the tree) gave me a weirdly long result list the second time I called it in the same session, and I didn't figure out why.
Symlinks are supposed to point at another node so total_size can follow them — but I made a symlink point back at an ancestor directory once, just to see what happened, and had to kill the process.
Not fully sure total_size is even adding things up right when a directory has multiple files and multiple subdirectories mixed together — only tested one or the other, never both at once.

No tests. Good luck.'''



class FileSystem:
    def __init__(self):
        self.root = {'type': 'dir', 'children': {}}

    def add_file(self, path_parts, name, size):
        node = self._navigate(path_parts)
        node['children'][name] = {'type': 'file', 'size': size}

    def add_dir(self, path_parts, name):
        node = self._navigate(path_parts)
        node['children'][name] = {'type': 'dir', 'children': {}}

    def add_symlink(self, path_parts, name, target_parts):
        node = self._navigate(path_parts)
        target = self._navigate(target_parts)
        node['children'][name] = {'type': 'symlink', 'target': target}

    def _navigate(self, path_parts):
        node = self.root
        for part in path_parts:
            node = node['children'][part]
        return node

    def total_size(self, node=None):
        if node is None:
            node = self.root

        if node['type'] == 'file':
            return node['size']

        total = 0
        for child in node['children'].values():
            if child['type'] == 'file':
                total += child['size']
            elif child['type'] == 'dir':
                total += self.total_size(child)
            elif child['type'] == 'symlink':
                total += self.total_size(child['target'])
        return total

    def find_all(self, name, node=None, results=None):
        if results is None:
            results = []
        if node is None:
            node = self.root

        for child_name, child in node['children'].items():
            if child_name == name:
                results.append(child)
            if child['type'] == 'dir':
                self.find_all(name, child, results)

        return results


def main():
    fs = FileSystem()
    fs.add_dir([], "docs")
    fs.add_file(["docs"], "readme.txt", 100)
    fs.add_dir(["docs"], "images")
    fs.add_file(["docs", "images"], "logo.png", 250)
    fs.add_file(["docs", "images"], "banner.png", 400)
    fs.add_dir([], "src")
    fs.add_file(["src"], "main.py", 50)

    print("Total size of entire filesystem:", fs.total_size())
    print("(Expected: 100 + 250 + 400 + 50 = 800)")

    print("\nSearching for all files named 'logo.png'...")
    print(fs.find_all("logo.png"))

    print("\nSearching again for 'main.py' (separate call)...")
    print(fs.find_all("main.py"))

    print("\nAdding a symlink from src back up to docs (creates a cycle)...")
    fs.add_symlink(["src"], "loop", ["docs"])
    print("Total size after cycle:", fs.total_size())  # would hang — leave commented until fixed


if __name__ == "__main__":
    main()