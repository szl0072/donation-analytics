import sys, math



class InputStream:
    def __init__(self, percent):
        
        self.donationList = []
        # store the percentile from the percentile input file
        self.percent = percent
        self.numberOfTransactions = 0
        self.totalAmount = 0

    def add(self, num):
        """
        Adds a num into the donation list.
        :type num: number
        :rtype: void
        """

        self.donationList.append(num)
        self.numberOfTransactions += 1
        self.totalAmount += num


    def percentile(self):
        """
        Returns the percentile base on the nearest-rank method {\displaystyle n=\left\lceil {\frac {P}{100}}\times N\right\rceil .}
        :rtype: int
        """

        index = int(math.ceil(float(self.percent)/100 * len(self.donationList)))
        self.donationList = sorted(self.donationList)
        return self.donationList[index - 1]

    # def totalAmount(self):
    #     return sum(self.donationList)

class Transaction(object):
    def __init__(self, data):
        info = data.split('|')
        self.cmte_id = info[0]

        #print(info)

        if len(info[10]) >= 5:
            if info[10][:5].isdigit():
                self.zipcode = info[10][:5]
        else:
            self.zipcode = None

        self.name = info[7] if info[7] != '' else ''
        self.transaction_date = info[13]
        self.transaction_amount = float(info[14]) if info[14] != '' else info[14]
        self.other_id = None if info[15] == '' else info[15]


    def valid(self):
        return self.other_id is None and \
               self.cmte_id != '' and \
               self.transaction_amount != '' and \
               self.name != ''

    def validate_date(self):
        date = self.transaction_date
        if len(date) != 8 or not date.isdigit():
            return False
        mm, dd, yy = int(date[0:2]), int(date[2:4]), int(date[4:8])
        
        if mm == 0 or mm > 12 or dd == 0 or dd > 31 or yy < 1900:
            return False
        if mm in [4, 6, 9, 11] and dd == 31:
            return False
        if (mm == 2 and dd >= 30) or ((yy % 4 != 0) and mm == 2 and dd >= 29):
            return False
        # store the year info
        self.yy = yy    
        return True

    def validate_zipcode(self):
        return self.zipcode is not None

    def __str__(self):
        return '(' + self.cmte_id + ',' + self.name + ',' + self.zipcode + ',' + self.transaction_date + ',' + \
               self.transaction_amount + self.other_id + ')'


def main():
    if len(sys.argv) - 1 != 3:
        raise Exception("Arguments should be three. two input data file paths, and one output file path")


    # input file 
    percentile_file = sys.argv[2]

    # get the info for percentile
    with open(percentile_file) as f:
        percent = f.readline()
        try:
            percent = int(percent)
        except Exception as e:
            print("percent has to be an integer in 1 - 100")
            print(str(e))
            sys.exit()


    percentile_by_zip_path = sys.argv[3]

    # map to store the key: value
    # key is zip + name
    # value is donation year 
    zip_map = dict()

    # list of output result
    zip_stream_result = []

    inputObject = InputStream(percent)
    with open(sys.argv[1]) as f:
        for line in f:
            t = Transaction(line)

            if t.valid() and t.validate_date() and t.validate_zipcode():
                # key is the zipcode + name to identify unique donor
                key = t.zipcode + t.name

                if key not in zip_map:

                    zip_map[key] = t.yy
                # if we saw this donor before     
                elif key in zip_map and zip_map[key] < t.yy:

                    inputObject.add(t.transaction_amount)



                    zip_stream_result.append([t.cmte_id, t.zipcode, str(t.yy), str(round(inputObject.percentile())),
                                   str(round(inputObject.totalAmount)),
                                   str(inputObject.numberOfTransactions)])
                # if the order is out of order chronologically, we want to update the ealiest year in the key map, for that donor 
                elif key in zip_map and zip_map[key] > t.yy:
                    zip_map[key] = t.yy

    # output required values by zipcode to file
    with open(percentile_by_zip_path, 'w') as f:
        for res in zip_stream_result:
            f.write('|'.join(res) + '\n')

if __name__ == "__main__":
    main()
