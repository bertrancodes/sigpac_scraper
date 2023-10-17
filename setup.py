import yaml
from pathlib import Path
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.opera import OperaDriverManager

gecko_driver = GeckoDriverManager().install()
chrome_driver = ChromeDriverManager().install()
opera_driver = OperaDriverManager().install()

drivers = {
        'gecko': gecko_driver,
        'chrome': chrome_driver,
        'opera': opera_driver
        }   

yaml_file = Path(Path(__file__).parent, 'config', 'drivers.yaml')
print(yaml_file)
yaml_file.parent.mkdir(parents = True, exist_ok = True)

with open(yaml_file, 'w') as stream:
    yaml.safe_dump(drivers, stream)
