import xmlschema
import xml.etree.ElementTree as ET
import pandas as pd
import os

# 🔧 Read values from Excel sheets into a dictionary of dictionaries
def read_values_from_excel(file_path):
    excel_data = pd.read_excel(file_path, sheet_name=None)
    all_values = {}

    for sheet_name, df in excel_data.items():
        sheet_values = dict(zip(df['Field'], df['Value']))
        all_values[sheet_name] = sheet_values

    return all_values

# 🎨 Pretty-print the XML
def indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

# 🧠 Recursive element builder with attribute support
def build_element(name, schema_element, values):
    # Base element with attributes
    elem_values = values.get(name, {})
    attributes = {}

    # Collect attributes like tc from keys ending with "_tc"
    for k, v in elem_values.items():
        if k.endswith('_tc') and k[:-3] in elem_values:
            continue  # Skip attribute definitions handled later
        if f"{k}_tc" in elem_values:
            attributes['tc'] = str(elem_values[f"{k}_tc"])

    element = ET.Element(name, attrib=attributes if attributes else {})

    # If simple element, add text content
    if schema_element.type.is_simple():
        element.text = str(elem_values.get(name, ''))
    elif schema_element.type.is_complex():
        if schema_element.type.content_type_label == 'complex':
            for sub_element in schema_element.type.content.iter_elements():
                tag = sub_element.name
                tag_val = elem_values.get(tag, '')
                attr_tc = elem_values.get(f"{tag}_tc", None)

                if sub_element.type.is_complex():
                    child = build_element(tag, sub_element, values)
                    element.append(child)
                else:
                    attribs = {}
                    if attr_tc:
                        attribs['tc'] = str(attr_tc)
                    child = ET.SubElement(element, tag, attrib=attribs)
                    child.text = str(tag_val)

    return element

# 🔁 Build full XML tree
def generate_xml_from_xsd_with_excel(xsd_path, excel_file_path, output_path="output.xml"):
    if not os.path.exists(xsd_path):
        print(f"❌ XSD file not found: {xsd_path}")
        return
    if not os.path.exists(excel_file_path):
        print(f"❌ Excel file not found: {excel_file_path}")
        return

    try:
        schema = xmlschema.XMLSchema(xsd_path)
        root_elem = next(iter(schema.elements.values()))
        values = read_values_from_excel(excel_file_path)

        root = build_element(root_elem.name, root_elem, values)

        # Format and save XML
        indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ XML generated and saved to: {output_path}")

        # Validate XML
        if schema.is_valid(output_path):
            print("✅ XML is valid according to the XSD.")
        else:
            print("❌ XML is NOT valid! Errors:")
            for error in schema.iter_errors(output_path):
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")

# 🚀 Main
if __name__ == "__main__":
    print("=== XSD to XML Generator from Excel ===")
    xsd_file = input("Enter path to your XSD file: ").strip()
    excel_file = input("Enter path to your Excel file: ").strip()
    generate_xml_from_xsd_with_excel(xsd_file, excel_file)
