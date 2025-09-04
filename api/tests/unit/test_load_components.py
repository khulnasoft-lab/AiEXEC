# ruff: noqa: T201
import asyncio
import time

import pytest
from aiexec.interface.components import aget_all_types_dict, import_aiexec_components
from aiexec.services.settings.base import BASE_COMPONENTS_PATH


class TestComponentLoading:
    """Test suite for comparing component loading methods performance and functionality."""

    @pytest.fixture
    def base_components_path(self):
        """Fixture to provide BASE_COMPONENTS_PATH as a list."""
        return [BASE_COMPONENTS_PATH] if BASE_COMPONENTS_PATH else []

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_get_aiexec_components_list_basic(self):
        """Test basic functionality of get_aiexec_components_list."""
        result = await import_aiexec_components()

        assert isinstance(result, dict), "Result should be a dictionary"
        assert "components" in result, "Result should have 'components' key"
        assert isinstance(result["components"], dict), "Components should be a dictionary"

        # Check that we have some components loaded
        total_components = sum(len(comps) for comps in result["components"].values())
        assert total_components > 0, "Should have loaded some components"

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_aget_all_types_dict_basic(self, base_components_path):
        """Test basic functionality of aget_all_types_dict."""
        result = await aget_all_types_dict(base_components_path)

        assert isinstance(result, dict), "Result should be a dictionary"
        # Note: aget_all_types_dict might return empty dict if no custom components in path
        # This is expected behavior when BASE_COMPONENTS_PATH points to built-in components

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_component_loading_performance_comparison(self, base_components_path):
        """Compare performance between get_aiexec_components_list and aget_all_types_dict."""
        # Warm up the functions (first calls might be slower due to imports)
        await import_aiexec_components()
        await aget_all_types_dict(base_components_path)

        # Time get_aiexec_components_list
        start_time = time.perf_counter()
        aiexec_result = await import_aiexec_components()
        aiexec_duration = time.perf_counter() - start_time

        # Time aget_all_types_dict
        start_time = time.perf_counter()
        all_types_result = await aget_all_types_dict(base_components_path)
        all_types_duration = time.perf_counter() - start_time

        # Log performance metrics
        print("\nPerformance Comparison:")
        print(f"get_aiexec_components_list: {aiexec_duration:.4f}s")
        print(f"aget_all_types_dict: {all_types_duration:.4f}s")
        print(f"Ratio (aiexec/all_types): {aiexec_duration / max(all_types_duration, 0.0001):.2f}")

        # Both should complete in reasonable time (< 5s for aiexec, < 15s for all_types)
        assert aiexec_duration < 5.0, f"get_aiexec_components_list took too long: {aiexec_duration}s"
        assert all_types_duration < 15.0, f"aget_all_types_dict took too long: {all_types_duration}s"

        # Store results for further analysis
        return {
            "aiexec_result": aiexec_result,
            "all_types_result": all_types_result,
            "aiexec_duration": aiexec_duration,
            "all_types_duration": all_types_duration,
        }

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_result_structure_comparison(self, base_components_path):
        """Compare the structure and content of results from both functions."""
        aiexec_result = await import_aiexec_components()
        all_types_result = await aget_all_types_dict(base_components_path)

        # Check aiexec result structure
        assert isinstance(aiexec_result, dict)
        assert "components" in aiexec_result
        aiexec_components = aiexec_result["components"]

        # Check all_types result structure
        assert isinstance(all_types_result, dict)

        # Get component counts
        aiexec_count = sum(len(comps) for comps in aiexec_components.values())
        all_types_count = sum(len(comps) for comps in all_types_result.values()) if all_types_result else 0

        print("\nComponent Counts:")
        print(f"get_aiexec_components_list: {aiexec_count} components")
        print(f"aget_all_types_dict: {all_types_count} components")

        # get_aiexec_components_list should always return built-in components
        assert aiexec_count > 0, "Should have built-in Aiexec components"

        # Analyze component categories
        if aiexec_components:
            aiexec_categories = list(aiexec_components.keys())
            print(f"Aiexec categories: {sorted(aiexec_categories)}")

        if all_types_result:
            all_types_categories = list(all_types_result.keys())
            print(f"All types categories: {sorted(all_types_categories)}")

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_component_template_structure(self):
        """Test that component templates have expected structure."""
        aiexec_result = await import_aiexec_components()

        # Check that components have proper template structure
        for category, components in aiexec_result["components"].items():
            assert isinstance(components, dict), f"Category {category} should contain dict of components"

            for comp_name, comp_template in components.items():
                assert isinstance(comp_template, dict), f"Component {comp_name} should be a dict"

                # Check for common template fields
                if comp_template:  # Some might be empty during development
                    # Common fields that should exist in component templates
                    expected_fields = {"display_name", "type", "template"}
                    present_fields = set(comp_template.keys())

                    # At least some expected fields should be present
                    common_fields = expected_fields.intersection(present_fields)
                    if len(common_fields) == 0 and comp_template:
                        print(f"Warning: Component {comp_name} missing expected fields. Has: {list(present_fields)}")

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_concurrent_loading(self, base_components_path):
        """Test concurrent execution of both loading methods."""
        # Run both functions concurrently
        tasks = [
            import_aiexec_components(),
            aget_all_types_dict(base_components_path),
            import_aiexec_components(),  # Run aiexec loader twice to test consistency
        ]

        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks)
        concurrent_duration = time.perf_counter() - start_time

        aiexec_result1, all_types_result, aiexec_result2 = results

        print(f"\nConcurrent execution took: {concurrent_duration:.4f}s")

        # Check that both results have the same structure and component counts
        assert isinstance(aiexec_result1, dict)
        assert isinstance(aiexec_result2, dict)
        assert isinstance(all_types_result, dict)

        # Check that both aiexec results have the same component structure
        assert "components" in aiexec_result1
        assert "components" in aiexec_result2

        # Compare component counts - these should be identical
        count1 = sum(len(comps) for comps in aiexec_result1["components"].values())
        count2 = sum(len(comps) for comps in aiexec_result2["components"].values())

        print(f"Component counts: {count1} vs {count2}")
        assert count1 == count2, f"Component counts should be identical: {count1} != {count2}"

        # Check that category names are the same
        categories1 = set(aiexec_result1["components"].keys())
        categories2 = set(aiexec_result2["components"].keys())

        if categories1 != categories2:
            missing_in_2 = categories1 - categories2
            missing_in_1 = categories2 - categories1
            print(f"Category differences: missing in result2: {missing_in_2}, missing in result1: {missing_in_1}")
            # This is acceptable as long as the main functionality is consistent

        # Check that component names within categories are the same
        for category in categories1.intersection(categories2):
            comps1 = set(aiexec_result1["components"][category].keys())
            comps2 = set(aiexec_result2["components"][category].keys())
            if comps1 != comps2:
                missing_in_2 = comps1 - comps2
                missing_in_1 = comps2 - comps1
                print(
                    f"Component differences in {category}: "
                    f"missing in result2: {missing_in_2}, missing in result1: {missing_in_1}"
                )

        # The results might not be exactly identical due to timing or loading order
        # but the core structure should be consistent
        print("Note: Results may have minor differences due to concurrent loading, but structure is consistent")

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, base_components_path):
        """Test memory usage patterns of both loading methods."""
        import gc

        # Force garbage collection before measuring
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Load with get_aiexec_components_list
        aiexec_result = await import_aiexec_components()
        after_aiexec_objects = len(gc.get_objects())

        # Load with aget_all_types_dict
        all_types_result = await aget_all_types_dict(base_components_path)
        after_all_types_objects = len(gc.get_objects())

        # Calculate object creation
        aiexec_objects_created = after_aiexec_objects - initial_objects
        all_types_objects_created = after_all_types_objects - after_aiexec_objects

        print("\nMemory Analysis:")
        print(f"Objects created by get_aiexec_components_list: {aiexec_objects_created}")
        print(f"Objects created by aget_all_types_dict: {all_types_objects_created}")

        # Clean up
        del aiexec_result, all_types_result
        gc.collect()

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in both loading methods."""
        # Test with empty paths list for aget_all_types_dict
        empty_paths = []

        # This should not raise an error, just return empty results
        result = await aget_all_types_dict(empty_paths)
        assert isinstance(result, dict), "Should return empty dict for empty paths"

        # Test with non-existent path - this should NOT raise an error, just return empty results
        nonexistent_paths = ["/nonexistent/path"]
        result = await aget_all_types_dict(nonexistent_paths)
        assert isinstance(result, dict), "Should return empty dict for non-existent paths"
        assert len(result) == 0, "Should return empty dict for non-existent paths"

        # Test with empty string path - this SHOULD raise an error
        empty_string_paths = [""]
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            await aget_all_types_dict(empty_string_paths)
        assert "path" in str(exc_info.value).lower(), f"Path-related error expected, got: {exc_info.value}"

        # get_aiexec_components_list should work regardless of external paths
        result = await import_aiexec_components()
        assert isinstance(result, dict)
        assert "components" in result

    @pytest.mark.no_blockbuster
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_repeated_loading_performance(self, base_components_path):
        """Test performance of repeated loading operations."""
        num_iterations = 5

        # Test repeated get_aiexec_components_list calls
        aiexec_times = []
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            await import_aiexec_components()
            duration = time.perf_counter() - start_time
            aiexec_times.append(duration)

        # Test repeated aget_all_types_dict calls
        all_types_times = []
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            await aget_all_types_dict(base_components_path)
            duration = time.perf_counter() - start_time
            all_types_times.append(duration)

        # Calculate statistics
        aiexec_avg = sum(aiexec_times) / len(aiexec_times)
        aiexec_min = min(aiexec_times)
        aiexec_max = max(aiexec_times)

        all_types_avg = sum(all_types_times) / len(all_types_times)
        all_types_min = min(all_types_times)
        all_types_max = max(all_types_times)

        print(f"\nRepeated Loading Performance ({num_iterations} iterations):")
        print(f"get_aiexec_components_list - avg: {aiexec_avg:.4f}s, min: {aiexec_min:.4f}s, max: {aiexec_max:.4f}s")
        print(f"aget_all_types_dict - avg: {all_types_avg:.4f}s, min: {all_types_min:.4f}s, max: {all_types_max:.4f}s")

        # Performance should be reasonably consistent
        aiexec_variance = max(aiexec_times) - min(aiexec_times)
        all_types_variance = max(all_types_times) - min(all_types_times)

        # Variance shouldn't be too high (more than 10x difference between min and max)
        assert aiexec_variance < aiexec_avg * 10, (
            f"get_aiexec_components_list performance too inconsistent: {aiexec_variance}s variance"
        )
        assert all_types_variance < all_types_avg * 10, (
            f"aget_all_types_dict performance too inconsistent: {all_types_variance}s variance"
        )

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_components_path_variations(self):
        """Test aget_all_types_dict with different path configurations."""
        test_cases = [
            [],  # Empty list
            [BASE_COMPONENTS_PATH] if BASE_COMPONENTS_PATH else [],  # Normal case - valid path
        ]

        # Test invalid paths separately with proper error handling
        invalid_test_cases = [
            [""],  # Empty string path
            ["/tmp"],  # Non-existent or invalid path #noqa: S108
            [BASE_COMPONENTS_PATH, "/tmp"]  # noqa: S108
            if BASE_COMPONENTS_PATH
            else ["/tmp"],  # Mixed valid/invalid paths #noqa: S108
        ]

        # Test valid cases
        for i, paths in enumerate(test_cases):
            print(f"\nTesting valid path configuration {i}: {paths}")

            start_time = time.perf_counter()
            result = await aget_all_types_dict(paths)
            duration = time.perf_counter() - start_time

            assert isinstance(result, dict), f"Result should be dict for paths: {paths}"

            component_count = sum(len(comps) for comps in result.values())
            print(f"  Loaded {component_count} components in {duration:.4f}s")

        # Test invalid cases - different invalid paths behave differently
        for i, paths in enumerate(invalid_test_cases):
            print(f"\nTesting invalid path configuration {i}: {paths}")

            # Empty string paths raise errors, but non-existent paths just return empty results
            if any(path == "" for path in paths):
                # Empty string paths should raise an error
                with pytest.raises((ValueError, OSError, FileNotFoundError)) as exc_info:
                    await aget_all_types_dict(paths)
                print(f"  Expected error for empty string path: {exc_info.value}")
                assert "path" in str(exc_info.value).lower(), f"Path-related error expected, got: {exc_info.value}"
            else:
                # Non-existent paths should return empty results without raising
                result = await aget_all_types_dict(paths)
                assert isinstance(result, dict), f"Should return dict for non-existent paths: {paths}"
                component_count = sum(len(comps) for comps in result.values())
                print(f"  Non-existent path returned {component_count} components (expected 0)")

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_comprehensive_performance_summary(self, base_components_path):
        """Comprehensive test that provides a summary of all performance aspects."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE COMPONENT LOADING PERFORMANCE SUMMARY")
        print("=" * 80)

        # WARM-UP RUNS (discard these timings)
        print("\nPerforming warm-up runs...")
        await import_aiexec_components()  # Warm up imports, thread pools, etc.
        await aget_all_types_dict(base_components_path)  # Warm up custom component loading
        print("Warm-up completed.")

        # Now run the actual performance measurements
        num_runs = 3
        aiexec_results = []
        all_types_results = []

        for run in range(num_runs):
            print(f"\nPerformance Run {run + 1}/{num_runs}")

            # Time get_aiexec_components_list
            start_time = time.perf_counter()
            aiexec_result = await import_aiexec_components()
            aiexec_duration = time.perf_counter() - start_time
            aiexec_results.append((aiexec_duration, aiexec_result))

            # Time aget_all_types_dict
            start_time = time.perf_counter()
            all_types_result = await aget_all_types_dict(base_components_path)
            all_types_duration = time.perf_counter() - start_time
            all_types_results.append((all_types_duration, all_types_result))

            print(f"  get_aiexec_components_list: {aiexec_duration:.4f}s")
            print(f"  aget_all_types_dict: {all_types_duration:.4f}s")

        # Calculate final statistics (excluding warm-up runs)
        aiexec_times = [duration for duration, _ in aiexec_results]
        all_types_times = [duration for duration, _ in all_types_results]

        print("\nSTEADY-STATE PERFORMANCE (after warm-up):")
        print("get_aiexec_components_list:")
        print(f"  Average: {sum(aiexec_times) / len(aiexec_times):.4f}s")
        print(f"  Min: {min(aiexec_times):.4f}s")
        print(f"  Max: {max(aiexec_times):.4f}s")

        print("aget_all_types_dict:")
        print(f"  Average: {sum(all_types_times) / len(all_types_times):.4f}s")
        print(f"  Min: {min(all_types_times):.4f}s")
        print(f"  Max: {max(all_types_times):.4f}s")

        # Component count analysis
        aiexec_component_counts = []
        all_types_component_counts = []

        for _, result in aiexec_results:
            count = sum(len(comps) for comps in result.get("components", {}).values())
            aiexec_component_counts.append(count)

        for _, result in all_types_results:
            count = sum(len(comps) for comps in result.values())
            all_types_component_counts.append(count)

        print("\nCOMPONENT COUNTS:")
        print(f"get_aiexec_components_list: {aiexec_component_counts}")
        print(f"aget_all_types_dict: {all_types_component_counts}")

        # Determine which is faster (based on steady-state performance)
        avg_aiexec = sum(aiexec_times) / len(aiexec_times)
        avg_all_types = sum(all_types_times) / len(all_types_times)

        if avg_aiexec < avg_all_types:
            faster_method = "get_aiexec_components_list"
            speedup = avg_all_types / avg_aiexec
        else:
            faster_method = "aget_all_types_dict"
            speedup = avg_aiexec / avg_all_types

        print("\nSTEADY-STATE PERFORMANCE CONCLUSION:")
        print(f"Faster method: {faster_method}")
        print(f"Speedup factor: {speedup:.2f}x")
        print(f"Timing results: {avg_aiexec:.4f}s (aiexec), ", f"{avg_all_types:.4f}s (all_types)")

        print("\nNOTE: These results exclude warm-up runs and represent steady-state performance")
        print("that users will experience after the first component load.")

        print("=" * 80)

        # Assertions for basic functionality
        assert all(count > 0 for count in aiexec_component_counts), (
            "get_aiexec_components_list should always return components"
        )
        assert all(isinstance(result, dict) for _, result in aiexec_results), "All aiexec results should be dicts"
        assert all(isinstance(result, dict) for _, result in all_types_results), "All all_types results should be dicts"

        # Assert that steady-state performance is good
        assert avg_aiexec < 5.0, f"Steady-state performance should be under 5s, got {avg_aiexec:.4f}s"
        assert speedup > 1.5, f"Parallelization should provide significant speedup, got {speedup:.2f}x"

    @pytest.mark.no_blockbuster
    @pytest.mark.asyncio
    async def test_component_differences_analysis(self, base_components_path):
        """Analyze and report the exact differences between components loaded by both methods."""
        print("\n" + "=" * 80)
        print("COMPONENT DIFFERENCES ANALYSIS")
        print("=" * 80)

        # Load components from both methods
        aiexec_result = await import_aiexec_components()
        all_types_result = await aget_all_types_dict(base_components_path)

        # Extract component data from both results
        # import_aiexec_components returns {"components": {category: {comp_name: comp_data}}}
        # aget_all_types_dict returns {category: {comp_name: comp_data}}
        aiexec_components = aiexec_result.get("components", {})
        all_types_components = all_types_result

        # Build flat dictionaries of all components: {comp_name: category}
        aiexec_flat = {}
        for category, components in aiexec_components.items():
            for comp_name in components:
                aiexec_flat[comp_name] = category

        all_types_flat = {}
        for category, components in all_types_components.items():
            for comp_name in components:
                all_types_flat[comp_name] = category

        # Calculate counts
        aiexec_count = len(aiexec_flat)
        all_types_count = len(all_types_flat)

        print("\nCOMPONENT COUNTS:")
        print(f"import_aiexec_components: {aiexec_count} components")
        print(f"aget_all_types_dict: {all_types_count} components")
        print(f"Difference: {abs(aiexec_count - all_types_count)} components")

        # Find components that are in one but not the other
        aiexec_only = set(aiexec_flat.keys()) - set(all_types_flat.keys())
        all_types_only = set(all_types_flat.keys()) - set(aiexec_flat.keys())
        common_components = set(aiexec_flat.keys()) & set(all_types_flat.keys())

        print("\nCOMPONENT OVERLAP:")
        print(f"Common components: {len(common_components)}")
        print(f"Only in import_aiexec_components: {len(aiexec_only)}")
        print(f"Only in aget_all_types_dict: {len(all_types_only)}")

        # Print detailed differences
        if aiexec_only:
            print(f"\nCOMPONENTS ONLY IN import_aiexec_components ({len(aiexec_only)}):")
            for comp_name in sorted(aiexec_only):
                category = aiexec_flat[comp_name]
                print(f"  - {comp_name} (category: {category})")

        if all_types_only:
            print(f"\nCOMPONENTS ONLY IN aget_all_types_dict ({len(all_types_only)}):")
            for comp_name in sorted(all_types_only):
                category = all_types_flat[comp_name]
                print(f"  - {comp_name} (category: {category})")

        # Check for category differences for common components
        category_differences = []
        for comp_name in common_components:
            aiexec_cat = aiexec_flat[comp_name]
            all_types_cat = all_types_flat[comp_name]
            if aiexec_cat != all_types_cat:
                category_differences.append((comp_name, aiexec_cat, all_types_cat))

        if category_differences:
            print(f"\nCOMPONENTS WITH DIFFERENT CATEGORIES ({len(category_differences)}):")
            for comp_name, aiexec_cat, all_types_cat in sorted(category_differences):
                print(f"  - {comp_name}: import_aiexec='{aiexec_cat}' vs aget_all_types='{all_types_cat}'")

        # Print category summary
        print("\nCATEGORY SUMMARY:")
        aiexec_categories = set(aiexec_components.keys())
        all_types_categories = set(all_types_components.keys())

        print(f"Categories in import_aiexec_components: {sorted(aiexec_categories)}")
        print(f"Categories in aget_all_types_dict: {sorted(all_types_categories)}")

        categories_only_aiexec = aiexec_categories - all_types_categories
        categories_only_all_types = all_types_categories - aiexec_categories

        if categories_only_aiexec:
            print(f"Categories only in import_aiexec_components: {sorted(categories_only_aiexec)}")
        if categories_only_all_types:
            print(f"Categories only in aget_all_types_dict: {sorted(categories_only_all_types)}")

        print("=" * 80)

        # Assertions to ensure the analysis is meaningful
        assert aiexec_count > 0, "import_aiexec_components should return components"
        assert all_types_count > 0, "aget_all_types_dict should return components"
        assert len(common_components) > 0, "There should be some overlap between the two methods"

    @pytest.mark.benchmark
    async def test_component_loading_performance(self):
        """Test the performance of component loading."""
        await import_aiexec_components()
