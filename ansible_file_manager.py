# ansible_file_manager.py

import os
import yaml

def load_rules(rules_file):
    """Loads Ansible-like rules from a YAML file."""
    with open(rules_file, 'r') as f:
        rules = yaml.safe_load(f)
    return rules

def apply_rules(rules, base_dir):
    """Applies Ansible-like rules to files and directories."""
    for rule in rules:
        path = os.path.join(base_dir, rule['path'])  # Combine base_dir and relative path
        state = rule.get('state', 'present')  # Default to 'present' if state is not specified
        file_type = rule.get('file_type', 'file') #Default file_type to file, can be directory
        content = rule.get('content')
        owner = rule.get('owner')
        group = rule.get('group')
        mode = rule.get('mode')
        recurse = rule.get('recurse', False) # default to false, if not specified

        if file_type == 'directory':
            if state == 'present':
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True) #creates all necessary intermediate directories.
                    print(f"Created directory: {path}")

                if owner and group:
                    import shutil
                    shutil.chown(path, owner, group)
                    print(f"Changed ownership of directory {path} to {owner}:{group}")

                if mode:
                    os.chmod(path, int(mode, 8)) #Convert octal string to integer
                    print(f"Changed mode of directory {path} to {mode}")
            elif state == 'absent':
                if os.path.exists(path):
                    import shutil
                    shutil.rmtree(path)
                    print(f"Removed directory: {path}")

        elif file_type == 'file':
            if state == 'present':
                if content is not None:
                    with open(path, 'w') as f:
                        f.write(content)
                    print(f"Created/updated file: {path}")

                if owner and group:
                    import shutil
                    shutil.chown(path, owner, group)
                    print(f"Changed ownership of file {path} to {owner}:{group}")

                if mode:
                    os.chmod(path, int(mode, 8))
                    print(f"Changed mode of file {path} to {mode}")

            elif state == 'absent':
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Removed file: {path}")

        if recurse and file_type == 'directory' and state == 'present':
            if 'children' in rule:
                apply_rules(rule['children'], path) #Recursively apply rules to children.

def main():
    """Main function to load and apply rules."""
    rules_file = 'file_rules.yml'  # Replace with your rules file
    base_dir = './managed_files'  # Replace with your base directory

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    rules = load_rules(rules_file)
    apply_rules(rules, base_dir)

if __name__ == "__main__":
    main()