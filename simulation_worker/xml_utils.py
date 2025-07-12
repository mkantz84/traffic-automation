import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def update_vtypes_xml(accel, tau, startup_delay, xml_path):
    logger.info(f"Updating {xml_path} with accel={accel}, tau={tau}, startupDelay={startup_delay}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for vtype in root.findall(".//vType"):
        vtype.set("accel", str(accel))
        vtype.set("tau", str(tau))
        vtype.set("startupDelay", str(startup_delay))
    tree.write(xml_path)
    logger.info(f"{xml_path} updated successfully.") 