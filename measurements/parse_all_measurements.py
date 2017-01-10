from bs4 import BeautifulSoup
from evaluation import dc_evaluation


if __name__ == '__main__':
    soup = BeautifulSoup('<chips />', 'xml')
    #soup = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')

    dc_evaluation.evaluate(soup)

    open('processed_measurements.xml', 'wb').write(soup.prettify("utf-8"))
