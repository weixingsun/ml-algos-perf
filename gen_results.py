# -*- coding: utf-8 -*-
"""
gen_results.py


This script downloads UCI data matrices, executes model files, and concatenates
their results into results.md.

Contrinutors should run this script after adding (and testing) models in
a model file to regenerate results.md with the new, contributed model's
results.

Contributors can edit the global EXT_CMD_DICT dictionary to match file
extensions to commands on their machines.

"""

### imports
import os
import time
import UCIDataMatrixFetcher

### constants
DIV_BAR = '==================================================================='

### contributors edit dictionary below ########################################

EXT_CMD_DICT = {
    # update for commands on your machine
    # file extension:command on your machine
    'py':'python',
    'r':'Rscript'
}

###############################################################################

def gen_tables_md(ext_cmd_dict, listing):

    """ Calls all model files to generate markdown tables containing results
    from user contributed modeling scripts.

    Args:
        ext_cmd_dict: dictionary mapping file extensions to executable commands
        listing: list of directories in git repo

    """

    tic = time.time()
    print DIV_BAR
    print 'Executing modeling files ...'

    ### loop through dirs in git repo
    ### execute appropriate model files
    for entry in listing:
        if os.path.isdir(entry):
            try:
                ext, _ = entry.split('_')
            except ValueError:
                continue
            if ext != 'r': # will add R models later
                model_fname = '.'.join([entry + '_models', ext])
                cmd = ext_cmd_dict[ext]
                print 'Executing ' + ' '.join([cmd, model_fname]) + ' ...'
                os.chdir(entry)
                os.system(' '.join([cmd, model_fname]))
                os.chdir('..')
                
    print 'Model files executed in %.2f s.' % (time.time()-tic)

def concat_tables(listing):

    """ Concatenates individual markdown tables generated by each model file
    into results.md.

    Args:
        listing: list of directories in git repo

    """
    tic = time.time()
    print DIV_BAR
    print 'Concatenating results ...'

    ### conditionally delete and then open results.md file
    if os.path.exists('results.md'):
        os.remove('results.md')
    res_md = open('results.md', 'a')

    ### concat markdown results generated by model files into results.md
    for entry in listing:
        if os.path.isdir(entry):
            try:
                ext, _ = entry.split('_')
            except ValueError:
                continue
            if ext != 'r': # will add R models later
                md_table_fname = '.'.join([entry + '_models', 'txt'])
                md_table_path = str(os.sep).join([entry, md_table_fname])
                with open(md_table_path) as md_table:
                    for line in md_table:
                        res_md.write(line)
                res_md.write('\n\n')

    res_md.close()

    print 'Results concatenated in %.2f s.' % (time.time()-tic)

def main():

    """ Downloads data matrices from UCI using UCIDataMatrixFetcher.
        Determines folders in git repo.
        Generate results markdown table files by calling model files
            in gen_tables_md().
        Concatenates markdown table files in concat_tables().

    """

    ### downlaod data 
    uci_fetcher = UCIDataMatrixFetcher()

    for tsk_prfx in ['cla', 'reg']:
        tsk_mtrx_url_lst = uci_fetcher.fetch_task_matrix_url_list(tsk_prfx)
        data_folder_link_list = uci_fetcher.fetch_data_folder_links_list(
            tsk_mtrx_url_lst,
            tsk_prfx
        )
        uci_fetcher.fetch_data(data_folder_link_list, tsk_prfx)

    ### execute models and generate results    
    listing = os.listdir('.')
    gen_tables_md(EXT_CMD_DICT, listing)
    concat_tables(listing)

if __name__ == '__main__':
    main()
