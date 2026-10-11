# test_engine.py
import random
from typing import Dict, Any

class ParameterizedTaskEngine:
    @staticmethod
    def generate_task(grade: str) -> Dict[str, Any]:
        """Генерирует задачу с уникальными входными данными и эталонным ответом."""
        if grade == "Junior":
            n = random.randint(10, 20)
            k = random.randint(2, 5)
            arr = [random.randint(1, 50) for _ in range(n)]
            
            # Задача: Длина макс подпоследовательности, где |a[i] - a[i-1]| <= k
            expected = ParameterizedTaskEngine._solve_max_subseq(arr, k)
            prompt = (
                f"Дан массив из {n} целых чисел: {arr}. "
                f"Найдите максимальную длину непрерывной подпоследовательности, "
                f"в которой разность соседних элементов не превышает {k}."
            )
            return {"task_id": "subseq_diff", "prompt": prompt, "answer": str(expected)}
        
        elif grade == "Middle":
            n = random.randint(15, 30)
            target = random.randint(40, 100)
            arr = [random.randint(5, 35) for _ in range(n)]
            
            # Задача: Количество пар элементов с суммой == target
            count = 0
            seen = {}
            for x in arr:
                count += seen.get(target - x, 0)
                seen[x] = seen.get(x, 0) + 1
            
            prompt = f"Дан массив из {n} элементов: {arr}. Найдите число пар элементов, сумма которых равна {target}."
            return {"task_id": "two_sum_count", "prompt": prompt, "answer": str(count)}

        else: # Senior
            n = random.randint(20, 40)
            arr = [random.randint(1, 100) for _ in range(n)]
            # Задача: Количество инверсий в массиве
            inv = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if arr[i] > arr[j]:
                        inv += 1
            prompt = f"Дан массив из {n} элементов: {arr}. Определите точное количество инверсий в данном массиве."
            return {"task_id": "inversions_count", "prompt": prompt, "answer": str(inv)}

    @staticmethod
    def _solve_max_subseq(arr, k):
        if not arr: return 0
        max_l = 1
        curr_l = 1
        for i in range(1, len(arr)):
            if abs(arr[i] - arr[i-1]) <= k:
                curr_l += 1
                max_l = max(max_l, curr_l)
            else:
                curr_l = 1
        return max_l

    @staticmethod
    def evaluate_test(score_percentage: float) -> Dict[str, Any]:
        """Определяет решение по грейду на основе порогов ТЗ."""
        if score_percentage >= 70.0:
            return {"status": "CONFIRMED", "message": "Грейд успешно подтвержден."}
        elif score_percentage < 40.0:
            return {"status": "DOWNGRADE_SUGGESTED", "message": "Тест не пройден. Рекомендуется выбрать грейд ниже."}
        else:
            return {"status": "FAILED", "message": "Тест не сдан. Попробуйте снова через установленный период."}