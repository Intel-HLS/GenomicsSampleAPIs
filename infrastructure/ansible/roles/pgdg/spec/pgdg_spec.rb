# vi: set ft=ruby :

require 'spec_helper'

redhat = ['redhat']

if redhat.include?(os[:family])

  describe yumrepo('pgdg') do
    it { should exist }
  end

end
