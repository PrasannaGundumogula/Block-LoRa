"""
Block-LoRA Setup Verification
Checks if all dependencies are installed correctly
"""
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (requires 3.10+)")
        return False

def check_package(package_name, import_name=None):
    """Check if Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (run: pip install {package_name})")
        return False

def check_node():
    """Check Node.js installation"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✓ Node.js {version}")
        return True
    except FileNotFoundError:
        print("❌ Node.js not found (install from nodejs.org)")
        return False

def check_hardhat():
    """Check if Hardhat is installed"""
    try:
        result = subprocess.run(['npx', 'hardhat', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Hardhat")
            return True
        else:
            print("❌ Hardhat (run: npm install)")
            return False
    except FileNotFoundError:
        print("❌ npx not found")
        return False

def check_contract_compiled():
    """Check if smart contract is compiled"""
    from pathlib import Path
    artifacts_path = Path("artifacts/contracts/BlockLoRA.sol/BlockLoRA.json")
    
    if artifacts_path.exists():
        print("✓ Smart contract compiled")
        return True
    else:
        print("❌ Smart contract not compiled (run: npx hardhat compile)")
        return False

def main():
    print("="*60)
    print("  Block-LoRA Setup Verification")
    print("="*60)
    
    checks = []
    
    print("\n--- Core Requirements ---")
    checks.append(check_python_version())
    checks.append(check_node())
    
    print("\n--- Python Packages ---")
    checks.append(check_package("torch"))
    checks.append(check_package("transformers"))
    checks.append(check_package("peft"))
    checks.append(check_package("datasets"))
    checks.append(check_package("web3"))
    checks.append(check_package("requests"))
    
    print("\n--- Blockchain Tools ---")
    checks.append(check_hardhat())
    checks.append(check_contract_compiled())
    
    print("\n" + "="*60)
    
    if all(checks):
        print("✓ All checks passed! Ready to run demo.")
        print("\nNext steps:")
        print("  1. Terminal 1: npx hardhat node")
        print("  2. Terminal 2: python demo.py")
    else:
        print("❌ Some checks failed. Please install missing dependencies.")
        print("\nQuick fix:")
        print("  pip install -r requirements.txt")
        print("  npm install")
        print("  npx hardhat compile")
    
    print("="*60)

if __name__ == "__main__":
    main()
