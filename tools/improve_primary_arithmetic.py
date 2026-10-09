"""Expand generic elementary arithmetic into concrete place-value working."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def addition(values, sw=False):
    names = ["moja", "makumi", "mamia", "maelfu", "makumi ya maelfu", "mamia ya maelfu", "mamilioni"] if sw else ["ones", "tens", "hundreds", "thousands", "ten-thousands", "hundred-thousands", "millions"]
    steps, carry = [], 0
    for column in range(max(len(str(value)) for value in values)):
        digits = [(value // (10 ** column)) % 10 for value in values]
        terms = digits + ([carry] if carry else [])
        total = sum(terms)
        digit, next_carry = total % 10, total // 10
        expression = " + ".join(map(str, terms)) + f" = {total}"
        name = names[column] if column < len(names) else str(10 ** column)
        if sw:
            step = f"Safu ya {name}: {expression}. Andika {digit}."
            if next_carry:
                step += f" Peleka {next_carry} kwenye safu inayofuata."
        else:
            step = f"{name.capitalize()} column: {expression}. Write {digit}."
            if next_carry:
                step += f" Carry {next_carry} to the next column."
        steps.append(step)
        carry = next_carry
    if carry:
        steps.append(f"Andika baki lililopelekwa, {carry}, upande wa kushoto." if sw else f"Write the remaining carry, {carry}, on the left.")
    result = sum(values)
    steps.append(f"Ukisoma tarakimu kutoka kushoto kwenda kulia unapata {result}." if sw else f"Read the digits from left to right: {result}.")
    return steps


def subtraction(left, right, sw=False):
    names = ["moja", "makumi", "mamia", "maelfu", "makumi ya maelfu", "mamia ya maelfu", "mamilioni"] if sw else ["ones", "tens", "hundreds", "thousands", "ten-thousands", "hundred-thousands", "millions"]
    digits = list(map(int, str(left)[::-1]))
    steps = []
    for column in range(len(digits)):
        subtract = (right // (10 ** column)) % 10
        name = names[column] if column < len(names) else str(10 ** column)
        if digits[column] < subtract:
            lender = column + 1
            while digits[lender] == 0:
                lender += 1
            digits[lender] -= 1
            for between in range(lender - 1, column, -1):
                digits[between] = 9
            before = digits[column]
            digits[column] += 10
            steps.append(f"Safu ya {name}: {before} haitoshi kutoa {subtract}. Azima kupitia safu za kushoto ili kupata {digits[column]}." if sw else f"{name.capitalize()} column: {before} is too small to subtract {subtract}. Regroup from the columns on its left to make {digits[column]}.")
        value = digits[column] - subtract
        steps.append(f"Safu ya {name}: {digits[column]} - {subtract} = {value}; andika {value}." if sw else f"{name.capitalize()} column: {digits[column]} - {subtract} = {value}; write {value}.")
    result = left - right
    steps.append(f"Soma matokeo: {result}. Uhakiki: {result} + {right} = {left}." if sw else f"Read the result: {result}. Check: {result} + {right} = {left}.")
    return steps


def numbers_for_addition(node):
    if isinstance(node, ast.Constant) and type(node.value) is int and node.value >= 0:
        return [node.value]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = numbers_for_addition(node.left), numbers_for_addition(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def improve():
    manifest = json.loads((ROOT / "exams/catalogue.json").read_text(encoding="utf-8"))["papers"]
    changed = []
    for filename, info in manifest.items():
        if info["subject"] != "Mathematics":
            continue
        source = ROOT / "answer_keys/solutions" / (Path(filename).stem + ".json")
        if not source.exists():
            continue
        data = json.loads(source.read_text(encoding="utf-8"))
        count = 0
        for question in data["questions"]:
            steps = question["steps"]
            generic = any("Align" in step or "regrouping from the next column" in step for step in steps)
            checks = question.get("math_checks", [])
            if not generic or len(checks) != 1:
                continue
            node = ast.parse(checks[0]["expression"], mode="eval").body
            values = numbers_for_addition(node)
            sw = data.get("language") == "sw"
            if values and len(values) > 1 and max(values) < 10 ** 7:
                question["steps"] = addition(values, sw)
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub) and isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                left, right = node.left.value, node.right.value
                if type(left) is not int or type(right) is not int or not 0 <= right <= left < 10 ** 7:
                    continue
                question["steps"] = subtraction(left, right, sw)
            else:
                continue
            count += 1
        if count:
            data.pop("visual_reviewed", None)
            data.pop("visual_review_pdf_sha256", None)
            temporary = source.with_suffix(".writing")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(source)
            changed.append({"exam": filename, "expanded_solutions": count})
    print(json.dumps({"papers": len(changed), "expanded_solutions": sum(p["expanded_solutions"] for p in changed)}, indent=2))


if __name__ == "__main__":
    improve()
