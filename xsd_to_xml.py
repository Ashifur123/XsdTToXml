import xmlschema
import xml.etree.ElementTree as ET
import pandas as pd
import os

# 🔧 Read values from Excel file
def read_values_from_excel(file_path):
    df = pd.read_excel(file_path)
    values = dict(zip(df['Field'], df['Value']))
    return values

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

# 🧠 Generate XML from XSD and Excel values
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
        root = ET.Element(root_elem.name)

        # Read values from Excel
        values = read_values_from_excel(excel_file_path)


        if root_elem.type.is_complex():
            for child in root_elem.type.content.iter_elements():
                value = values.get(child.name, '')
                child_elem = ET.SubElement(root, child.name)
                child_elem.text = str(value)
        else:
            root.text = str(values.get(root_elem.name, ''))

        # Format and save XML
        indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ XML generated and saved to: {output_path}")

        # ✅ Validate against XSD
        if schema.is_valid(output_path):
            print("✅ XML is valid according to the XSD.")
        else:
            print("❌ XML is NOT valid! Errors:")
            for error in schema.iter_errors(output_path):
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")

# 🚀 Main script execution
if __name__ == "__main__":
    print("=== XSD to XML Generator from Excel ===")
    xsd_file = input("Enter path to your XSD file: ").strip()
    excel_file = input("Enter path to your Excel file: ").strip()
    generate_xml_from_xsd_with_excel(xsd_file, excel_file)
