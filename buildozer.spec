[app]

title = Carrom AI
package.name = carromai
package.domain = org.carromai

source.dir = .
source.include_exts = py,png,jpg,jpeg

version = 1.0

requirements = python3,pygame-ce

orientation = landscape

fullscreen = 0

android.api = 34
android.minapi = 23
android.archs = arm64-v8a

p4a.local_recipes = %(source.dir)s/p4a-recipes

[buildozer]

log_level = 2
warn_on_root = 1
