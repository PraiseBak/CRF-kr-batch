#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
if __name__ == '__main__':
    #parser.add_argument("mode", help="the model file name. (output)")

    #args = parser.parse_args()
    #test_datafile = convert.convert_to_input(args.datafile)

    #mode = args.mode
    #test_datafile = "small_train.data"
    datafile = "mini_Sejong.txt"
    model = "small_model.json"
    import os
    crf = LinearChainCRF()
#   crf.train(args.datafile, args.modelfile)
    crf.train(datafile, model)
