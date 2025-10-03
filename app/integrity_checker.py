"""
Integrity checking module.
Handles verification and auto-fix of audiobook collections.
"""

import subprocess
import sys
from config import AUDIOBOOK_DIR


class IntegrityChecker:
    """Manages integrity verification and auto-fix operations."""
    
    def run_integrity_check_and_fix(self):
        """Run integrity verification with automatic fixes before downloading."""
        try:
            print("\n🔍 Running integrity verification and auto-fix...")
            sys.stdout.flush()
            
            # Run the streamlined verification script
            result = subprocess.run([
                "python", "/app/auto_integrity_check.py"
            ], capture_output=True, text=True)
            
            if result.returncode >= 0:  # 0 = no issues, >0 = issues found and fixed, -1 = error
                # Show the output from the integrity check
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            print(f"   {line}")
                            sys.stdout.flush()
                
                if result.returncode > 0:
                    print(f"✅ Integrity check fixed {result.returncode} issues")
                    sys.stdout.flush()
                elif result.returncode == 0:
                    print("✅ Integrity check completed - no issues found")
                    sys.stdout.flush()
            else:
                print(f"⚠️  Integrity check encountered errors")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                sys.stdout.flush()
                
        except Exception as e:
            print(f"Error running integrity check: {e}")
            sys.stdout.flush()


# Global integrity checker instance
integrity_checker = IntegrityChecker()