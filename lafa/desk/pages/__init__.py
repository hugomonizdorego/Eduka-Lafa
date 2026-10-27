"""Pages of Lafa Desktop. Each page has `route`, `show_route(params)` and `retranslate()`."""
import importlib

MODULES = {
    "home": ("home", "HomePage"), "encyclopedia": ("encyclopedia", "EncyclopediaPage"), "category": ("encyclopedia", "CategoryPage"),
    "item": ("article", "ItemPage"), "map": ("mapview", "MapPage"), "timeline": ("timeline", "TimelinePage"),
    "places": ("places", "PlacesPage"), "calendar": ("calendar", "CalendarPage"), "quiz": ("millionaire", "MillionairePage"),
    "language": ("language", "LanguagePage"), "paths": ("paths", "PathsPage"), "sources": ("sources", "SourcesPage"),
    "data": ("data", "DataPage"), "settings": ("settings", "SettingsPage"), "about": ("about", "AboutPage"), "search": ("search", "SearchPage"),
}

def page_class(route):
    module, name = MODULES[route]
    return getattr(importlib.import_module(f"{__name__}.{module}"), name)
