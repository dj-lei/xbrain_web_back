import csv
import sys
import collections
import pandas as pd
import os


class PinmuxConfig(object):
    """
    Class that parses the cvs with the pinmux config and creates a
    dts file with the configuration for
    - gpio group
    - gpio number
    - Pull-up/down
    - Slew rate
    - Impedance
    """
    def __init__(self, originfile, infile, outfile, script, asic, revision, debug=False):
        self.originfile = originfile
        self.infile = infile
        self.outfile = outfile
        self.script = 'create_pinmux_config_one_click_9_18.py'
        self.asic = asic
        self.not_valid = 0xFF;
        # The names below are used to fech the column name
        # this will make this script more robus when the colomn names
        # are changing.
        self.pin_name = 'pinpackage'
        self.gpionumber_name = 'GPIO number'
        self.gpiogroup_name = 'GPIO group'
        self.slewrate_name = 'slewrate'
        self.pull_name = 'pull-up'
        self.impedance_name = 'impedance'
        self.ie_name ='Intended Input Enable'
        self.dir_name = 'intended DIR'
        self.alt_func_name = 'Boot I/O-mux'
        self.out_val_name = 'Output value'
        self.keys = [self.pin_name,
                     self.ie_name,
                     self.gpionumber_name,
                     self.gpiogroup_name,
                     self.slewrate_name,
                     self.pull_name,
                     self.impedance_name,
                     self.dir_name,
                     self.alt_func_name,
                     self.out_val_name]
        self.column_dict = {}
        self.debug = debug
        if asic == 'xenon':
            self.docno = '1/10262-ROZ1041534/42 Uen Rev ' + revision
        elif asic == 'radon':
           self.docno = '1/155 19-CXS 101 765/1 Uen Rev ' + revision
        else:
            sys.exit("Unknown asic")

    def _get_alt_func(self, val):
        try:
            return int('0x' + val, 16)
        except:
            return self.not_valid

    def _get_direction(self, val):
        try:
            return int(val, 2)
        except:
            if "Input" in val or "IN" in val:
                return 0
            elif "Output" in val or "OUT" in val:
                return 1

        return self.not_valid

    def _get_int_from_binary(self, val):
        val = val.replace('\"', '')
        try:
            return int(val, 2)
        except:
            return self.not_valid

    def _get_int(self, val):
        try:
            return int(val)
        except:
            return self.not_valid

    def _create_32bit_entry(self, varname, val):
         """
         This method will create an entry of the
         form
         name#u32 = <value>;
         """
         return "\t\t\t\t\t\t" + varname.lower() + "#u32 = <" + str(hex(val)) + ">;\n"

    def _get_val_from_string(self, val):
        """
        input to this method is string
        of the form "ab"
        the value of a and b is returned.
        """
        val = val.replace('\"', '')
        val_a = self._get_int_from_binary(val[0])
        val_b = self._get_int_from_binary(val[1])
        return val_a, val_b

    def _create_entry(self, name, gpio_number, values):
        entry = "" + \
        "\t\t\t\t\tpin" + str(gpio_number)  + " { " +  "/* " + name + " */\n"
        for key, val in dict(values).items():
            entry = entry + self._create_32bit_entry(key, val)
        entry = entry + "\t\t\t\t\t};\n"
        return entry

    def _compare(self, a, b):
        """
        Compare the strings a and b in lower case
        and all the newlines, " and whitespaces removed.
        """
        _a = a.lower().replace('\"', '').replace('\n','').replace(' ', '')
        _b = b.lower().replace('\"', '').replace('\n','').replace(' ', '')
        if _a in _b:
            return True
        return False

    def _get_column_name(self, key):
        try:
            return self.column_dict[key]
        except:
            return ""

    def _set_column_names(self, row):
        for key, value in dict(row).items():
            for k in self.keys:
                if self._compare(k, key):
                    self.column_dict[k] = key

    def _register_values(self, row):
        name = row[self._get_column_name(self.pin_name)]
        ie_name = row[self._get_column_name(self.ie_name)]
        gpio_group = int(row[self._get_column_name(self.gpiogroup_name)])
        # Note:
        # special handling of gpio_number
        # as the excel have a column named EVC GPIO number
        # and one named GPIO number.
        gpio_number = int(row['GPIO number'])
        #gpio_number = int(row[self._get_column_name(self.gpionumber_name)])
        slew_rate = self._get_int(row[self._get_column_name(self.slewrate_name)])
        pull_en, pull_sel  = self._get_val_from_string(row[self._get_column_name(self.pull_name)])
        impsel1, impsel2 = self._get_val_from_string(row[self._get_column_name(self.impedance_name)])
        input_enable = self._get_int(ie_name)
        dir_val = self._get_direction(row[self._get_column_name(self.dir_name)])
        alt_func = self._get_alt_func(row[self._get_column_name(self.alt_func_name)])
        out_val = self._get_int(row[self._get_column_name(self.out_val_name)])
        dict_entry = collections.OrderedDict()
        dict_entry['slew'] =  slew_rate
        dict_entry['pull_en'] = pull_en
        dict_entry['pull_sel'] = pull_sel
        dict_entry['impsel1'] =  impsel1
        dict_entry['impsel2'] = impsel2
        dict_entry['input_enable'] = input_enable
        dict_entry['dir'] = dir_val
        dict_entry['alt_func'] = alt_func
        dict_entry['out_val'] = out_val
        entry = self._create_entry(name, gpio_number, dict_entry)

        if self.debug:
            print ("{" + str(gpio_group) + ","  +\
            str(gpio_number) + "," +\
            str(slew_rate) + "," +\
            str(pull_en) + "," +\
            str(pull_sel) + "," +\
            str(impsel1) + "," +\
            str(impsel2) + "," +\
            str(input_enable) + "," +\
            str(dir_val) + "," +\
            str(alt_func) + "," +\
            str(out_val) + "},")
        return entry, "group" + str(gpio_group)

    def _get_meta_data(self, subgroups, no_pins_per_group):
        tabs ="\t\t\t\t\t"
        meta = "\t\t\t\t" + "metainfo {\n" + \
            tabs + "groups#u32 = <" + str(len(subgroups)) + ">;\n" + \
            tabs + "subgroups#u32 = <" + ' '.join(str(i) for i in subgroups) + ">;\n" + \
            tabs + "pins#u32 = <" +  ' '.join(str(i) for i in  no_pins_per_group) + ">;\n" + \
            "\t\t\t\t" + "};\n"
        return meta

    def _write_file(self, asic, pins, no_pins_per_group):
        with open('ru/tmp/temp.txt', 'w') as outfile:
            outfile.write("/dts-v1/;\n")
            outfile.write("/{\n\tsys {\n")
            outfile.write("\t/** This is autogenerated by " + self.script + "\n\t ** from " + self.originfile + ".\n")
            outfile.write("\t ** Input is the excel document " + self.docno + " in csv format.\n")
            outfile.write("\t ** A pin value that is n/a, unavailable, or protected has value " + str(hex(self.not_valid)) + ".\n\t **/\n")
            outfile.write("\t\tpinmux {\n")
            if asic == 'radon':
                outfile.write("\t\t\tradon_1_slave")
            elif asic == 'xenon':
                outfile.write("\t\t\txenon_11_slave")
            outfile.write(" { /*start*/\n")
            subgroups = [1 if (x-1) < 32 else int((x-1) / 32 + 1) for x in no_pins_per_group]
            meta = self._get_meta_data(subgroups,  no_pins_per_group)
            outfile.write(meta)

            for key, value in dict(pins).items():
                outfile.write("\t\t\t\t" + key + " {\n")
                outfile.write(value)
                outfile.write("\t\t\t\t};\n")
            outfile.write("\t\t\t};/*end*/\n")
            outfile.write("\t\t};\n")
            outfile.write("\t};\n")
            outfile.write("};")
        print("Created " + self.outfile + " from " + self.originfile)

    def _add_pin(self, no_pins_per_group, index):
        if index + 1 > len(no_pins_per_group):
            no_pins_per_group.append(1)
        else:
            no_pins_per_group[index] = 1 + no_pins_per_group[index]
        return  no_pins_per_group

    def create(self):
        pins = collections.OrderedDict()
        no_pins_per_group = []
        with open(self.infile) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            got_columns = False
            for row in csv_reader:
                if not got_columns:
                    self._set_column_names(row)
                    got_columns = True
                regs, group = self._register_values(row)
                group_as_int = group.replace('group', '')
                self._add_pin(no_pins_per_group, int(group_as_int))
                if group in pins:
                    pins[group] = pins[group] + regs
                else:
                    pins[group] = regs
        self._write_file(self.asic, pins, no_pins_per_group)