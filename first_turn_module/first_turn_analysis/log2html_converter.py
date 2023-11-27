"""
This script is designed to convert log data into a readable HTML format.
It reads log files, organizes the data based on predefined prompts,
and then generates an HTML file presenting this organized data in
a structured and readable format.

Functions:
- read_and_organize_data: Reads log file and organizes data by prompts.
- generate_html_and_write_file: Generates HTML content from the organized
    log data and writes it to an output file.
- transform_log_to_html: Main function that orchestrates the reading,
    organizing, and HTML file generation process.

Usage:
This script is intended to be used with log files in JSON format.
The expected structure of the log entries should include 'Opener_prompt'
as a key. Modify the script accordingly if the log file structure differs.

Example:
To use the script, call the transform_log_to_html function with the
input log file and the desired output HTML file name as arguments.
transform_log_to_html("path_to_example.log", 'path_to_example.html')
"""
import html
import json
from collections import defaultdict, OrderedDict


def organize_logs(input_file):
    """ Reads the log file and organizes the data by test cases. """
    prompt_index = OrderedDict()
    logs_by_test_case = defaultdict(list)

    # Reading data from the input file and organizing it
    with open(input_file, 'r') as input_f:
        for line in input_f:
            log = json.loads(line)
            if log['Opener_prompt'] not in prompt_index:
                prompt_index[log['Opener_prompt']] = len(prompt_index) + 1
            test_case = log['text']
            # if test_case is empty, replace it with a space
            test_case = " " if not test_case else test_case
            logs_by_test_case[test_case].append(log)

    return prompt_index, logs_by_test_case


def generate_html_content(prompt_index, logs_by_test_case):
    """ Generates HTML content from categorized logs. """
    # Starting the HTML content
    html_content = """
<!DOCTYPE html>
<html>

<head>
    <title>Chat Opener Evaluation</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script>
        function sortSection(sectionElement) {
            Array.from(sectionElement.children)
                .map(function (element) { return { element: element, index: parseInt(element.textContent.match(/\d+/)[0]) }; })
                .sort(function (a, b) { return a.index - b.index; })
                .forEach(function (obj) { sectionElement.appendChild(obj.element); });
        }

        function showActive() {
            $('.case-response').hide();
            $('#activePromptSection .dropdown-item').each(function () {
                $('[data-prompt-id="' + this.id + '"]').show(); // Show only the content for the selected prompt
            });
            $('.test-case').hide();
            $('#activeCaseSection .dropdown-item').each(function () {
                $('[data-case-id="' + this.id + '"]').show(); // Show only the content for the selected case
            });
        }

        function toggleStatus(itemElement) {
            var activeSectionId = "active" + itemElement.role + "Section";
            var isActive = itemElement.closest('.collapse').id === activeSectionId;
            var targetSectionId = isActive ? "in" + activeSectionId : activeSectionId;
            var targetSection = document.getElementById(targetSectionId);

            // Move to target section
            targetSection.appendChild(itemElement);

            // Sort prompts in the target section
            sortSection(targetSection);

            // Show the active prompts related content if the prompt is active
            showActive();
        }

    </script>
    <style>
        .sticky-top {
            position: sticky;
            top: 0;
            z-index: 1020;
        }

        .scrollable-menu {
            height: auto;
            max-height: 200px;
            /* Adjust as needed */
            overflow-x: hidden;
            overflow-y: auto;
        }

        /* Styles for toggle buttons */
        .toggle-button {
            font-weight: bold;
        }

        /* Subdued styles for prompt items */
        .prompt-item {
            padding-left: 20px;
            /* Indentation for sub-menu items */
            color: #495057;
            /* Slightly darker than default Bootstrap text color */
        }

        .arrow {
            display: inline-block;
            width: 0;
            height: 0;
            margin-left: 5px;
            vertical-align: middle;
            border-top: 5px solid;
            border-right: 5px solid transparent;
            border-left: 5px solid transparent;
        }

        .collapse.show+.dropdown-item .arrow {
            transform: rotate(180deg);
            /* Arrow points up when section is expanded */
        }
    </style>
</head>

<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light sticky-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Chat Opener Evaluation</a>
            <ul class="navbar-nav">
                <!-- Dropdown for Prompts -->
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownPrompts" role="button"
                        data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
                        Prompts
                    </a>
                    <ul class="dropdown-menu scrollable-menu" aria-labelledby="navbarDropdownPrompts">
                        <!-- Active Prompts Section -->
                        <li>
                            <a class="dropdown-item" href="#" data-bs-toggle="collapse"
                                data-bs-target="#activePromptSection">Active Prompts<span class="arrow"></span></a>
                            <div id="activePromptSection" class="toggle-button collapse show">
    """

    # Adding prompts to the dropdown
    for prompt, index in prompt_index.items():
        html_content += f"<a id='prompt{index}' class='dropdown-item prompt-item' role='Prompt' \
            data-bs-toggle='popover' data-bs-container='body' data-bs-placement='left' \
            data-bs-content='{html.escape(prompt)}' href='#'>Prompt {index}</a>\n"
    # Continuing with the test cases dropdown
    html_content += """
                            </div>
                        </li>

                        <!-- Inactive Prompts Section -->
                        <li>
                            <a class="dropdown-item" href="#" data-bs-toggle="collapse"
                                data-bs-target="#inactivePromptSection">Inactive Prompts<span class="arrow"></span></a>
                            <div id="inactivePromptSection" class="toggle-button collapse">
                            </div>
                        </li>

                    </ul>
                </li>
                <!-- Dropdown for Test Cases -->
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownTestCases" role="button"
                        data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
                        Test Cases
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end scrollable-menu" aria-labelledby="navbarDropdownTestCases">
                        <!-- Active Cases Section -->
                        <li>
                            <a class="dropdown-item" href="#" data-bs-toggle="collapse"
                                data-bs-target="#activeCaseSection">Active Cases<span class="arrow"></span></a>
                            <div id="activeCaseSection" class="toggle-button collapse show">
    """

    # Adding test cases to the dropdown
    for i, test_case in enumerate(logs_by_test_case.keys()):
        html_content += f"<a id='case{i+1}' class='dropdown-item case-item' role='Case' \
            data-bs-toggle='popover' data-bs-container='body' data-bs-placement='left' \
            data-bs-content='{html.escape(test_case)}' href='#'>Test Case {i+1}</a>\n"
    # Closing the dropdowns and starting the main content area
    html_content += """
                            </div>
                        </li>

                        <!-- Inctive Cases Section -->
                        <li>
                            <a class="dropdown-item" href="#" data-bs-toggle="collapse"
                                data-bs-target="#inactiveCaseSection">Inactive Cases<span class="arrow"></span></a>
                            <div id="inactiveCaseSection" class="toggle-button collapse">
                            </div>

                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    <div class="container mt-4">
        <div id="testCasesContent">
    """

    # Adding content for each test case
    for i, (test_case, logs) in enumerate(logs_by_test_case.items()):
        html_content += f"<div class='test-case' data-case-id='case{i+1}'><h3>Test Case {i+1}: {test_case}</h3>\n"
        for log in logs:
            prompt_number = prompt_index[log['Opener_prompt']]
            html_content += f"<p class='case-response' data-prompt-id='prompt{prompt_number}'>Prompt {prompt_number}: {log['response']}</p>\n"
        html_content += "</div>\n"

    # Closing the HTML tags
    html_content += """
        </div>
    </div>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>

    <script>
        // Adding click event listeners to prompts
        document.addEventListener("DOMContentLoaded", function () {
            document.querySelectorAll('.prompt-item, .case-item').forEach(function (item) {
                item.addEventListener('click', function () {
                    toggleStatus(this);
                });
            });
        });
        $(document).ready(function () {
            // Listen to collapse events on the collapsible sections
            $('#activePromptSection, #inactivePromptSection, #activeCaseSection, #inactiveCaseSection').on('show.bs.collapse', function () {
                // Rotate arrow up when the section is shown
                $(this).prev('.dropdown-item').find('.arrow').css('transform', 'rotate(180deg)');
            }).on('hide.bs.collapse', function () {
                // Rotate arrow down when the section is hidden
                $(this).prev('.dropdown-item').find('.arrow').css('transform', '');
            });

            // Show the popover related content
            $('[data-bs-toggle="popover"]').popover({ trigger: "hover" });
        });

    </script>
</body>

</html>
    """
    return html_content


def transform_log_to_html(input_file, output_file):
    """ Main function to transform log data into an HTML file. """
    prompt_index, logs_by_test_case = organize_logs(input_file)

    # Starting the HTML content
    html_content = generate_html_content(prompt_index, logs_by_test_case)

    # Writing the HTML content to the output file
    with open(output_file, 'w') as output_f:
        output_f.write(html_content)
