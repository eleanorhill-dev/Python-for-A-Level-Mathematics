import traceback

def evaluate_code(submitted_code, test_cases):
    results = []
    try:
        for case in test_cases:
            input_value = case["input"]
            expected_output = case["output"]

            # Prepare an execution environment
            execution_env = {"input_value": input_value}
            exec(submitted_code, {}, execution_env)

            # Extract the result
            result = execution_env.get('result', None)
            results.append(result == expected_output)

        return all(results)
    except Exception as e:
        return False, traceback.format_exc()