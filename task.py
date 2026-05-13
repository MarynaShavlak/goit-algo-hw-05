import timeit


# --- Boyer-Moore Algorithm ---
def build_shift_table(pattern):
    """Build the bad character shift table for the Boyer-Moore algorithm.

    Args:
        pattern: The substring pattern to search for.

    Returns:
        A dictionary mapping each character to its shift value.
    """
    shift_table = {}
    pattern_length = len(pattern)
    for index, char in enumerate(pattern[:-1]):
        shift_table[char] = pattern_length - index - 1
    shift_table.setdefault(pattern[-1], pattern_length)
    return shift_table


def boyer_moore_search(text, pattern):
    """Search for a pattern in text using the Boyer-Moore algorithm.

    Args:
        text: The main text to search within.
        pattern: The substring pattern to search for.

    Returns:
        The index of the first occurrence of the pattern, or -1 if not found.
    """
    shift_table = build_shift_table(pattern)
    pattern_length = len(pattern)
    text_index = 0

    while text_index <= len(text) - pattern_length:
        pattern_index = pattern_length - 1

        # Compare characters from the end of the pattern to the beginning
        while pattern_index >= 0 and text[text_index + pattern_index] == pattern[pattern_index]:
            pattern_index -= 1

        if pattern_index < 0:
            return text_index

        # Shift the text index based on the bad character table
        text_index += shift_table.get(text[text_index + pattern_length - 1], pattern_length)

    return -1


# --- Knuth-Morris-Pratt Algorithm ---
def compute_lps(pattern):
    """Compute the Longest Proper Prefix which is also Suffix (LPS) array.

    Args:
        pattern: The substring pattern to build the LPS array for.

    Returns:
        A list representing the LPS array for the given pattern.
    """
    lps = [0] * len(pattern)
    previous_lps_length = 0
    current_index = 1

    while current_index < len(pattern):
        if pattern[current_index] == pattern[previous_lps_length]:
            previous_lps_length += 1
            lps[current_index] = previous_lps_length
            current_index += 1
        else:
            if previous_lps_length != 0:
                previous_lps_length = lps[previous_lps_length - 1]
            else:
                lps[current_index] = 0
                current_index += 1

    return lps


def kmp_search(text, pattern):
    """Search for a pattern in text using the Knuth-Morris-Pratt algorithm.

    Args:
        text: The main text to search within.
        pattern: The substring pattern to search for.

    Returns:
        The index of the first occurrence of the pattern, or -1 if not found.
    """
    lps = compute_lps(pattern)
    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if pattern[pattern_index] == text[text_index]:
            text_index += 1
            pattern_index += 1

        if pattern_index == len(pattern):
            return text_index - pattern_index
        elif text_index < len(text) and pattern[pattern_index] != text[text_index]:
            if pattern_index != 0:
                pattern_index = lps[pattern_index - 1]
            else:
                text_index += 1

    return -1


# --- Rabin-Karp Algorithm ---
def rabin_karp_search(text, pattern, base=256, modulus=101):
    """Search for a pattern in text using the Rabin-Karp algorithm.

    Args:
        text: The main text to search within.
        pattern: The substring pattern to search for.
        base: The base value for polynomial hashing.
        modulus: The modulus value to avoid hash overflow.

    Returns:
        The index of the first occurrence of the pattern, or -1 if not found.
    """
    text_length = len(text)
    pattern_length = len(pattern)
    hash_multiplier = pow(base, pattern_length - 1) % modulus
    pattern_hash = 0
    text_window_hash = 0

    # Compute initial hash values for the pattern and the first text window
    for i in range(pattern_length):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % modulus
        text_window_hash = (base * text_window_hash + ord(text[i])) % modulus

    # Slide the pattern window over the text
    for i in range(text_length - pattern_length + 1):
        if pattern_hash == text_window_hash:
            if text[i:i + pattern_length] == pattern:
                return i

        # Recalculate hash for the next text window using rolling hash
        if i < text_length - pattern_length:
            text_window_hash = (base * (text_window_hash - ord(text[i]) * hash_multiplier) + ord(text[i + pattern_length])) % modulus
            if text_window_hash < 0:
                text_window_hash += modulus

    return -1


# --- Utility Functions ---
def load_text(filepath, encoding):
    """Load text content from a file.

    Args:
        filepath: Path to the text file.
        encoding: Character encoding of the file.

    Returns:
        The full text content of the file as a string.
    """
    with open(filepath, "r", encoding=encoding) as file:
        return file.read()


def measure_search_time(search_func, text, pattern, iterations=100):
    """Measure average execution time of a search function.

    Args:
        search_func: The search algorithm function to benchmark.
        text: The text to search within.
        pattern: The pattern to search for.
        iterations: Number of times to repeat the measurement.

    Returns:
        The average execution time per single search in seconds.
    """
    timer = timeit.Timer(lambda: search_func(text, pattern))
    total_time = timer.timeit(number=iterations)
    return total_time / iterations


def main():
    article_1_text = load_text("article_1.txt", "cp1251")
    article_2_text = load_text("article_2.txt", "utf-8-sig")

    # Substrings that actually exist in the articles
    existing_pattern_article_1 = "алгоритмів у бібліотеках"
    existing_pattern_article_2 = "рекомендаційної системи"
    # Fictional substring that does not exist in either article
    fictional_pattern = "абвгдежзиклмно_вигаданий_підрядок_12345"

    search_algorithms = {
        "Боєра-Мура": boyer_moore_search,
        "Кнута-Морріса-Пратта": kmp_search,
        "Рабіна-Карпа": rabin_karp_search,
    }

    benchmark_results = {}

    articles = [
        ("Стаття 1", article_1_text, existing_pattern_article_1),
        ("Стаття 2", article_2_text, existing_pattern_article_2),
    ]
    pattern_types = [
        ("існуючий", None),  # placeholder, will be replaced per article
        ("вигаданий", fictional_pattern),
    ]

    for article_name, article_text, existing_pattern in articles:
        benchmark_results[article_name] = {}
        for pattern_label, pattern in [("існуючий", existing_pattern), ("вигаданий", fictional_pattern)]:
            benchmark_results[article_name][pattern_label] = {}
            for algorithm_name, algorithm_func in search_algorithms.items():
                avg_time = measure_search_time(algorithm_func, article_text, pattern)
                benchmark_results[article_name][pattern_label][algorithm_name] = avg_time

    # --- Print results table ---
    print("=" * 80)
    print(f"{'Алгоритм':<25} {'Підрядок':<12} {'Стаття 1 (с)':<18} {'Стаття 2 (с)':<18}")
    print("=" * 80)

    for algorithm_name in search_algorithms:
        for pattern_label in ["існуючий", "вигаданий"]:
            time_article_1 = benchmark_results["Стаття 1"][pattern_label][algorithm_name]
            time_article_2 = benchmark_results["Стаття 2"][pattern_label][algorithm_name]
            print(f"{algorithm_name:<25} {pattern_label:<12} {time_article_1:<18.8f} {time_article_2:<18.8f}")
        print("-" * 80)

    # --- Build markdown report ---
    md_lines = ["# Висновки щодо ефективності алгоритмів пошуку підрядка\n"]
    md_lines.append("## Результати вимірювань\n")
    col_algo = 22
    col_pattern = 10
    col_time = 14

    header = (
        f"| {'Алгоритм':<{col_algo}} | {'Підрядок':<{col_pattern}} "
        f"| {'Стаття 1 (с)':<{col_time}} | {'Стаття 2 (с)':<{col_time}} |"
    )
    separator = (
        f"| {'-' * col_algo} | {'-' * col_pattern} "
        f"| {'-' * col_time} | {'-' * col_time} |"
    )
    md_lines.append(header)
    md_lines.append(separator)

    for algorithm_name in search_algorithms:
        for pattern_label in ["існуючий", "вигаданий"]:
            time_article_1 = benchmark_results["Стаття 1"][pattern_label][algorithm_name]
            time_article_2 = benchmark_results["Стаття 2"][pattern_label][algorithm_name]
            md_lines.append(
                f"| {algorithm_name:<{col_algo}} | {pattern_label:<{col_pattern}} "
                f"| {time_article_1:<{col_time}.8f} | {time_article_2:<{col_time}.8f} |"
            )

    md_lines.append("\n## Найшвидший алгоритм для кожного тексту\n")

    overall_time_totals = {name: 0 for name in search_algorithms}

    for article_name in ["Стаття 1", "Стаття 2"]:
        md_lines.append(f"### {article_name}\n")
        article_time_totals = {}
        for algorithm_name in search_algorithms:
            total_time = sum(
                benchmark_results[article_name][pattern_label][algorithm_name]
                for pattern_label in ["існуючий", "вигаданий"]
            )
            article_time_totals[algorithm_name] = total_time
            overall_time_totals[algorithm_name] += total_time

        fastest_algorithm = min(article_time_totals, key=article_time_totals.get)
        for algorithm_name, total_time in article_time_totals.items():
            marker = " **(найшвидший)**" if algorithm_name == fastest_algorithm else ""
            md_lines.append(f"- {algorithm_name}: {total_time:.8f} с{marker}")
        md_lines.append("")

    md_lines.append("## Загальний висновок\n")
    fastest_overall_algorithm = min(overall_time_totals, key=overall_time_totals.get)
    for algorithm_name, total_time in overall_time_totals.items():
        marker = " **(найшвидший)**" if algorithm_name == fastest_overall_algorithm else ""
        md_lines.append(f"- {algorithm_name}: {total_time:.8f} с{marker}")

    md_lines.append(
        f"\n**Загалом найшвидшим алгоритмом є {fastest_overall_algorithm}.**"
    )

    md_content = "\n".join(md_lines)

    with open("results.md", "w", encoding="utf-8") as results_file:
        results_file.write(md_content)

    print("\n" + md_content)
    print("\nРезультати збережено у файл results.md")


if __name__ == "__main__":
    main()
