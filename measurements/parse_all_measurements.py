from bs4 import BeautifulSoup
from evaluation import dc_evaluation, ac_evaluation


if __name__ == '__main__':
    #soup = BeautifulSoup('<chips />', 'xml')
    soup = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')

    dc_evaluation.evaluate(soup)
    #ac_evaluation.evaluate(soup)

    open('processed_measurements_out.xml', 'wb').write(soup.prettify("utf-8"))
