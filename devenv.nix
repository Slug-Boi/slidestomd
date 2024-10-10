{ pkgs, lib, config, inputs, ... }:

{
  languages.python = {
    enable = true;
    venv.enable = true;
    venv.requirements = ''
      Halo
      pytesseract
    '';
  };

  enterShell = ''
    echo "Entering shell with Python venv activated"
  '';
}

