#!/usr/bin/env python3
"""
Check what routes are registered in the FastAPI app
"""

import sys
sys.path.append('/app/backend')

from server import app

print("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{route.methods} {route.path}")
    elif hasattr(route, 'path'):
        print(f"MOUNT {route.path}")

print("\nLooking for aavana2 routes:")
aavana2_routes = [route for route in app.routes if hasattr(route, 'path') and 'aavana2' in route.path]
print(f"Found {len(aavana2_routes)} aavana2 routes:")
for route in aavana2_routes:
    print(f"  {route.methods} {route.path}")