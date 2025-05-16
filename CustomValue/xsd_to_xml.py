import xmlschema
import xml.etree.ElementTree as ET
import os

def read_values_from_file(file_path):
    values = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '=' not in line:
                continue
            key, val = line.split('=', 1)
            values[key.strip()] = val.strip()
    return values

def generate_xml_from_xsd_with_values_file(xsd_path, values_file_path, output_path="output.xml"):
    if not os.path.exists(xsd_path):
        print(f"❌ XSD file not found: {xsd_path}")
        return
    if not os.path.exists(values_file_path):
        print(f"❌ Values file not found: {values_file_path}")
        return

    try:
        schema = xmlschema.XMLSchema(xsd_path)
        root_elem = next(iter(schema.elements.values()))
        root = ET.Element(root_elem.name)

        # Read values from file
        values = read_values_from_file(values_file_path)

        if root_elem.type.is_complex():
            for child in root_elem.type.content.iter_elements():
                value = values.get(child.name, '')  # Default to empty string if not found
                child_elem = ET.SubElement(root, child.name)
                child_elem.text = value
        else:
            root.text = values.get(root_elem.name, '')

        # Write XML
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ XML generated and saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== XSD to XML Generator from Values File ===")
    xsd_file = input("Enter path to your XSD file: ").strip()
    values_file = input("Enter path to your values text file: ").strip()
    generate_xml_from_xsd_with_values_file(xsd_file, values_file)
