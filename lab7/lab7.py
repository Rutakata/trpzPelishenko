import inspect
import sys

import tabulate
import numpy


class ClassStats:
    def __init__(self):
        self.inheritance_depth = 0
        self.child_count = 0
        self.inherited_methods_count = 0
        self.overridden_methods_count = 0
        self.new_methods_count = 0
        self.visible_methods_count = 0
        self.private_methods_count = 0


class MetricCounter:

    def __init__(self, verbose=False):
        self._cached_inheritance: dict[type, int] = {}
        self.classes_stats: dict[type, ClassStats] = {}
        self._verbose = verbose

    def vprint(self, *args):
        if self._verbose:
            print(*args, sep=' ', end='\n', file=None)

    def count_class(self, class_tmp: type) -> ClassStats:
        class_metrics = ClassStats()
        class_metrics.child_count = len(class_tmp.__subclasses__())
        class_metrics.inheritance_depth = self.count_class_inheritance_depth(class_tmp)
        self.count_props(class_tmp, class_metrics)
        self.classes_stats[class_tmp] = class_metrics
        return class_metrics

    def count_class_inheritance_depth(self, class_tmp: type) -> int:
        if class_tmp in self._cached_inheritance:
            return self._cached_inheritance[class_tmp]
        if class_tmp.__base__ == object:
            inheritance_depth = 0
        else:
            inheritance_depth = self.count_class_inheritance_depth(class_tmp.__base__) + 1
        self._cached_inheritance[class_tmp] = inheritance_depth
        return inheritance_depth

    def count_props(self, class_tmp: type, out_stats: ClassStats):
        new_methods = 0
        inherited_methods = 0
        overridden_methods = 0
        visible_methods = 0
        private_methods = 0
        for name_c, obj_c in inspect.getmembers(class_tmp):
            if inspect.isroutine(obj_c):
                if name_c not in class_tmp.__dict__:
                    inherited_methods += 1
                    self.vprint(f'{name_c} inherited')
                elif any(name_c in super_class.__dict__ for super_class in class_tmp.mro()[1:]):
                    overridden_methods += 1
                    self.vprint(f'{name_c} overridden')
                else:
                    new_methods += 1
                    self.vprint(f'{name_c} new')
                if name_c.startswith(f'_{class_tmp.__name__}') and not name_c.endswith("_"):
                    private_methods += 1
                    self.vprint(f'{name_c} private')
                else:
                    visible_methods += 1
                    self.vprint(f'{name_c} visible')
        out_stats.new_methods_count = new_methods
        out_stats.overridden_methods_count = overridden_methods
        out_stats.inherited_methods_count = inherited_methods
        out_stats.visible_methods_count = visible_methods
        out_stats.private_methods_count = private_methods

    def get_polymorphism_factor(self) -> float:
        overriden_methods = 0
        denim = 0
        for class_tmp, stats in self.classes_stats.items():
            overriden_methods += stats.overridden_methods_count
            denim += stats.new_methods_count * stats.child_count
        if overriden_methods == 0 or denim == 0:
            return 0.0
        return overriden_methods / denim

    def get_method_inheritance_factor(self) -> float:
        inherited_methods = 0
        all_methods = 0
        for class_tmp, stats in self.classes_stats.items():
            inherited_methods += stats.overridden_methods_count
            all_methods += stats.new_methods_count + stats.inherited_methods_count + stats.overridden_methods_count
        if inherited_methods == 0 or all_methods == 0:
            return 0.0
        return inherited_methods / all_methods

    def get_closed_methods_factor(self) -> float:
        private_methods = 0
        all_methods = 0
        for class_tmp, stats in self.classes_stats.items():
            private_methods += stats.private_methods_count
            all_methods += stats.visible_methods_count + stats.private_methods_count
        if private_methods == 0 or all_methods == 0:
            return 0.0
        return private_methods / all_methods


def class_stats_to_row(class_tmp: type, stats: ClassStats):
    return [class_tmp.__name__, stats.inheritance_depth, stats.child_count]


if __name__ == '__main__':

    counter = MetricCounter()

    for name, obj in inspect.getmembers(sys.modules['numpy']):
        if inspect.isclass(obj):
            counter.count_class(obj)
    table_headers = ["Class Name", "Inheritance Depth", "Children Count"]
    print(tabulate.tabulate([class_stats_to_row(class_tmp, stats) for class_tmp, stats in
                             counter.classes_stats.items()], headers=table_headers, tablefmt="grid"))
    lib_factors = {"Closed Methods Factor": [counter.get_closed_methods_factor()],
                   "Method Inheritance Factor": [counter.get_method_inheritance_factor()],
                   "Polymorphism Factor": [counter.get_polymorphism_factor()]}
    lib_factors_headers = ["Closed Methods Factor", "Method Inheritance Factor", "Polymorphism Factor"]
    print(tabulate.tabulate(lib_factors, headers="keys", tablefmt="grid"))