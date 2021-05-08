import os
import csv
import re

import pdfplumber

PARENT_DIRECTORY = os.getcwd()
INVOICES_DIRECTORY = os.getcwd() + "/Invoices/"


def shift_parallel_lines(shift_type, shifter_data, grouped_lines):
    modified_grouped_lines = grouped_lines
    for line in modified_grouped_lines[shift_type]:
        for shift in shifter_data:
            if shift_type == "horizontal":
                if line["y_pos"] == shift[0]:
                    line["modifications"] = {
                        "y_pos_shift": shift[1]
                    }
            elif shift_type == "vertical":
                if line["x_pos"] == shift[0]:
                    line["modifications"] = {
                        "x_pos_shift": shift[1]
                    }
    return modified_grouped_lines


def find_parallel_shift_value(shift_type, locations_to_correct, grouped_lines):
    shifter_data = []

    locs_to_correct = locations_to_correct
    len_of_locs_to_correct = [[0] * len(i) for i in locations_to_correct]
    shift = [[0] * len(i) for i in locations_to_correct]

    for i, loc_group in enumerate(locations_to_correct):
        for line in grouped_lines[shift_type]:
            for j, loc in enumerate(loc_group):
                if shift_type == "horizontal":
                    if line["y_pos"] == loc:
                        len_of_locs_to_correct[i][j] += line["x_right"] - line["x_left"]
                elif shift_type == "vertical":
                    if line["x_pos"] == loc:
                        len_of_locs_to_correct[i][j] += line["y_bottom"] - line["y_top"]

    print(f"length of locs to correct: {len_of_locs_to_correct}")

    for i, loc_group in enumerate(locations_to_correct):
        max_length = max(len_of_locs_to_correct[i])
        max_length_index = len_of_locs_to_correct[i].index(max_length)
        max_length_loc = loc_group[max_length_index]
        for j, loc in enumerate(loc_group):
            if loc != max_length_loc:
                shift[i][j] = max_length_loc - loc
                shifter_data.append((loc, shift[i][j]))

    return shifter_data


def find_locations_for_parallel_shift(pos, grouped_lines):
    parallel_shift_tolerance = 1

    locations = list(set([y[pos] for y in grouped_lines]))  # List > Set > List for unique values
    locations.sort()

    locations_to_correct = []
    temp_locations = []

    for i in range(len(locations) - 1):
        if parallel_shift_tolerance >= (locations[i + 1] - locations[i]) > 0:
            temp_locations.append(locations[i])
        else:
            if len(temp_locations) != 0:
                temp_locations.append(locations[i])
                locations_to_correct.append(temp_locations)
                temp_locations = []

    print(f"Locations to correct: {locations_to_correct}")
    return locations_to_correct


def adjust_parallel_lines(grouped_lines):
    modified_grouped_lines = grouped_lines

    y_locations_to_correct = find_locations_for_parallel_shift("y_pos", grouped_lines["horizontal"])
    y_locations_to_correct_shift = find_parallel_shift_value("horizontal", y_locations_to_correct, grouped_lines)
    modified_grouped_lines = shift_parallel_lines("horizontal", y_locations_to_correct_shift, grouped_lines)

    x_locations_to_correct = find_locations_for_parallel_shift("x_pos", grouped_lines["vertical"])
    x_locations_to_correct_shift = find_parallel_shift_value("vertical", x_locations_to_correct, grouped_lines)
    print(f"shifter data: {x_locations_to_correct_shift}")
    modified_grouped_lines = shift_parallel_lines("vertical", x_locations_to_correct_shift, grouped_lines)

    return modified_grouped_lines


# CLASSIFICATION OF LINES INTO 3 GROUPS: HORIZONTAL, VERTICAL, OTHER
def classify_lines_by_type(lines):
    grouped_lines = {
        "horizontal": [],
        "vertical": [],
        "other": []
    }

    for line in lines:
        line_info = {}
        # HORIZONTAL LINES
        if line["height"] == 0:
            # line_info = {
            #     "y_pos": 0.00,
            #     "x_left": 0.00,
            #     "x_right": 0.00,
            #     "modifications": {
            #         "y_pos_shift": 0.00,
            #         "left_extension": 0.00,
            #         "right_extension": 0.00,
            #     }
            # }
            line_info["y_pos"] = line["top"]
            line_info["x_left"] = line["x0"]
            line_info["x_right"] = line["x1"]
            grouped_lines["horizontal"].append(line_info)

        # VERTICAL LINES
        elif line["width"] == 0:
            # line_info = {
            #     "x_pos": 0.00,
            #     "y_top": 0.00,
            #     "y_bottom": 0.00,
            #     "modifications": {
            #         "x_pos_shift": 0.00,
            #         "top_extension": 0.00,
            #         "bottom_extension": 0.00,
            #     }
            # }
            line_info["x_pos"] = line["x0"]
            line_info["y_top"] = line["top"]
            line_info["y_bottom"] = line["bottom"]
            grouped_lines["vertical"].append(line_info)

        # OTHER TYPES OF LINES
        else:
            pass

    return grouped_lines


# ANALYSING LINES DATA
# 1. GROUPING
# 2. FIXING
# 3. FINDING INTERSECTIONS
def analyse_lines(lines):
    # Resulting list of tuples representing intersection points
    modified_lines = []

    # Grouping lines into 3 categories: horizontal, vertical, other
    lines_grouped = classify_lines_by_type(lines)
    # print(f"Grouped lines:\n{lines_grouped}")

    modified_lines = adjust_parallel_lines(lines_grouped)
    print(modified_lines["horizontal"])

    print("VISIBLE LINES INFORMATION")
    print(f"Total line(s) found: {len(lines)}")
    print(f"horizontal lines: {len(lines_grouped['horizontal'])}\n"
          f"vertical lines: {len(lines_grouped['vertical'])}\n"
          f"other lines: {len(lines_grouped['other'])}")
    print("--")

    # # Adding points to resulting list
    # for line in lines:
    #     if (line["x0"], line["top"]) not in intersections:
    #         intersections.append((line["x0"], line["top"]))
    #
    #     if (line["x1"], line["bottom"]) not in intersections:
    #         intersections.append((line["x1"], line["bottom"]))
    #
    # # Printing number of intersection points
    # print(f"{len(intersections)} intersection point(s) found.")
    # # print(f"Intersection Points:\n{intersections}")

    return modified_lines


def analyse_pdf(pdf_file_path):
    # Opening pdf file with pdfplumber
    with pdfplumber.open(pdf_file_path) as pdf:
        # PDF properties
        metadata = pdf.metadata
        pages = pdf.pages

        # Analysing page data
        for page in pages:
            # Page properties: Basic info
            page_number = page.page_number
            page_width = page.width
            page_height = page.height
            print("--")
            print("PAGE INFORMATION")
            print(f"Page number: {page_number}\nPage width: {page_width}\nPage height: {page_height}")
            print("--")

            # Page properties: Visible lines
            page_lines = page.lines
            grouped_lines = classify_lines_by_type(page_lines)

            # Analyse lines and find intersections
            modified_lines = analyse_lines(page_lines)

            # Visual debugging
            page_image = page.to_image(resolution=300)
            printed_y_pos = []
            for h_line in modified_lines["horizontal"]:
                y_pos = h_line["y_pos"]
                try:
                    y_pos += h_line["modifications"]["y_pos_shift"]
                except KeyError:
                    pass
                printed_y_pos.append(y_pos)
                page_image.draw_hline(y_pos)
            printed_y_pos.sort()
            print(printed_y_pos)
            for v_line in modified_lines["vertical"]:
                page_image.draw_vline(v_line["x_pos"])
            # page_image.draw_circles(intersection_points)
            page_image.save(pdf_file_path[:-4] + "_vd.png", format="PNG")

            print(page.extract_text())
            break


for root, directories, files in os.walk(INVOICES_DIRECTORY):

    # Current working directory and count of files and folders
    print("----")
    print(f"Current working directory: {root}")
    print(f"{len(directories)} folder(s) found, {len(files)} file(s) found")
    print("----")

    # Looping through files and analysing pdf files
    for file in files:
        if file.endswith(".pdf"):
            # Creating file path
            file_path = os.path.join(root, file)
            print(f"Analysing file: {file_path}")

            # Analysing pdf file
            analyse_pdf(file_path)
