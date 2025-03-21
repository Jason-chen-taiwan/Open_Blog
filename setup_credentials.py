import os
import secrets
import string
import yaml

# 定義默認配置
DEFAULT_CONFIG = {
    'MYSQL_PASSWORD': 'yourpassword',
    'ADMIN_EMAIL': 'admin@example.com',
}

def generate_secret_key():
    """Generate a secure secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def reset_credentials():
    """Reset all credentials to default values."""
    print("\n=== Resetting Credentials to Default ===\n")
    setup_credentials(reset=True)
    print("All credentials have been reset to default values.")

def setup_credentials(reset=False):
    """Setup or reset all necessary credentials."""
    print("\n=== Blog Application Credentials Setup ===\n")
    
    if reset:
        mysql_password = DEFAULT_CONFIG['MYSQL_PASSWORD']
        admin_email = DEFAULT_CONFIG['ADMIN_EMAIL']
        print("Using default configuration:")
    else:
        # Get MySQL credentials
        mysql_password = input(f"Enter MySQL password (leave blank for '{DEFAULT_CONFIG['MYSQL_PASSWORD']}'): ").strip()
        mysql_password = mysql_password or DEFAULT_CONFIG['MYSQL_PASSWORD']
        
        # Get admin credentials
        admin_email = input(f"Enter admin email (leave blank for '{DEFAULT_CONFIG['ADMIN_EMAIL']}'): ").strip()
        admin_email = admin_email or DEFAULT_CONFIG['ADMIN_EMAIL']
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Load and update docker-compose files
    compose_files = ['docker-compose.yml', 'docker-compose.dev.yml', 'docker-compose.prod.yml']
    
    for compose_file in compose_files:
        try:
            with open(compose_file, 'r') as f:
                docker_compose = yaml.safe_load(f)
            
            # Update MySQL password
            if 'mysql' in docker_compose['services']:
                docker_compose['services']['mysql']['environment'].update({
                    'MYSQL_PASSWORD': mysql_password,
                })
            
            # Update web service environment
            if 'web' in docker_compose['services']:
                env_vars = docker_compose['services']['web'].get('environment', [])
                new_env_vars = []
                
                # Remove existing vars we want to update
                for var in env_vars:
                    if isinstance(var, str) and not any(var.startswith(x) for x in ['MYSQL_PASSWORD=', 'ADMIN_EMAIL=']):
                        new_env_vars.append(var)
                
                # Add updated variables
                new_env_vars.extend([
                    f'MYSQL_PASSWORD={mysql_password}',
                    f'ADMIN_EMAIL={admin_email}',
                    f'SECRET_KEY={secret_key}'
                ])
                
                docker_compose['services']['web']['environment'] = new_env_vars
            
            # Write updated configuration
            with open(compose_file, 'w') as f:
                yaml.dump(docker_compose, f, default_flow_style=False)
                
            print(f"Updated {compose_file}")
            
        except Exception as e:
            print(f"Error updating {compose_file}: {str(e)}")
    
    # Create/update .env file
    env_content = f"""
MYSQL_PASSWORD={mysql_password}
ADMIN_EMAIL={admin_email}
SECRET_KEY={secret_key}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content.strip())
    
    print("\n=== Credentials Setup Completed ===")
    print(f"MySQL Password: {mysql_password}")
    print(f"Admin Email: {admin_email}")
    print("\nConfiguration saved to:")
    print("- docker-compose.yml")
    print("- docker-compose.dev.yml")
    print("- docker-compose.prod.yml")
    print("- .env")
    print("\nYou can now run:")
    print("1. docker compose down -v")
    print("2. docker compose up -d")
    print("3. Check admin password in logs: docker compose logs web | grep 'Admin Account'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_credentials()
    else:
        setup_credentials()
