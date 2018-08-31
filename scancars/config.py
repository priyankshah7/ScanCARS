import configparser

config = configparser.ConfigParser()

config['DEFAULT'] = {
    'camtrackLower1': '150',
    'camtrackUpper1': '160',
    'camtrackLower2': '180',
    'camtrackUpper2': '190',
    'spec_exposuretime': '0.05',
    'spec_background_frames': '50',
    'spec_spectral_frames': '100',
    'hyp_exposuretime': '0.05',
    'hyp_background_frames': '50',
    'num_x_pix': '50',
    'num_y_pix': '10',
    'num_z_pix': '1',
    'xy_step': '0.3',
    'z_step': '0.5',
    'temp': '-80'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
