function main_getImage
    close all;clc;warning('off','all')
    
    % Data directory and file of interest - edit here to local
    dataDir='./Data/';
    fileName='pat0002_20161004_141027_5167.mat';
    
    % Define figure and axis 
    f=figure('units','normalized','position',[0.0000 0.0463 1.0000 0.9269]);
    set(f,'color','w','HitTest','off','WindowButtonDownFcn',@clicks_Callback,'ButtonDownFcn',@clicks_Callback,'KeyPressFcn',@keys_Callback,'MenuBar','none','ToolBar','none');
    Ax_SPE={subplot('position',[.030 .735 .350 .230]);subplot('position',[.030 .500 .350 .230]);subplot('position',[.030 .265 .350 .230]);subplot('position',[.030 .030 .350 .230]);subplot('position',[.030 .965 .350 .020])};
    Ax_EEG=subplot('position',[.415 .030 .560 .935]);
    
    % Declare global variables/parameters
    tc=25;
    w=10;
    Fs=200;
    channel_withspace_bipolar ={'Fp1-F7' 'F7-T3' 'T3-T5' 'T5-O1' '' 'Fp2-F8' 'F8-T4' 'T4-T6' 'T6-O2' '' 'Fp1-F3' 'F3-C3' 'C3-P3' 'P3-O1' '' 'Fp2-F4' 'F4-C4' 'C4-P4' 'P4-O2' '' 'Fz-Cz'  'Cz-Pz' '' 'EKG'};
    dt=2;
    zScale=1/150;
    col=[-10 25];
    colormap jet
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Main function
    % 1. Read data
    [seg,segTime,sdata]=fcn_readData(fileName);
    
    % 2. Parse data
    [tt,timeStamps,channel_withspace,seg_disp,DCoff]=fcn_getDataDisp(seg,tc,w,segTime);
    
    % 3. Plot EEG
    fcn_plotEEG(Ax_EEG,seg_disp,timeStamps);
    
    % 4. Plot spectrograms
    fcn_plotSpect(Ax_SPE,sdata);

    % 5. Export .png image
    print(f,strrep(fileName,'.mat','.png'),'-dpng');
   
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Local Callback functions
    function [seg,segTime,sdata]=fcn_readData(filename)
        % Get infor from file name
        filename=strrep(filename,'.mat','');
        iii=regexp(filename,'_');
        timeStampo = datetime(filename(iii(1)+1:iii(end)-1),'inputformat','yyyyMMdd_HHmmss');
        segTime=timeStampo+seconds(2*str2num(filename(iii(end)+1 : end))+1-5);
        
        % Read
        tmp=load([dataDir,filename],'data_50sec','spec_10min');
        seg=tmp.data_50sec;
        sdata=tmp.spec_10min;
        
        % Denoise
        [B1,A1]=butter(3,[.5 40]/(Fs/2));
        [B2,A2]=butter(3,[60-2.5 60+2.5]/(Fs/2),'stop');
        seg(isnan(seg))=0;
        seg=filtfilt(B1,A1,seg')';
        seg=filtfilt(B2,A2,seg')';     
    end
 
    function [tt,timeStamps,channel_withspace,seg_disp,DCoff]=fcn_getDataDisp(seg,tc,w,segTime)
        % Parse data for display - central 10sec on L-bipolar
        tto=tc*Fs-(w/2)*Fs+1;tt1=tc*Fs+(w/2)*Fs;tt=tto:tt1;
        seg=seg(:,tto:tt1);
        eeg=seg(1:19,:);
        ekg=-seg(20,:);
        gap=NaN(1,size(eeg,2));
        
        % L-bipolar
        seg=fcn_bipolar(eeg);
        seg_disp=[seg(1:4,:);gap;seg(5:8,:);gap;seg(9:12,:);gap;seg(13:16,:);gap;seg(17:18,:);gap;ekg];
        channel_withspace=channel_withspace_bipolar;
        M=size(seg_disp,1);
        DCoff=repmat(flipud((1:M)'),1,size(seg_disp,2));
        timeStamps=datestr(segTime+seconds(round(1/Fs:1:(w*Fs+1)/Fs)),'hh:MM:ss');
    end

    function dataBipolar=fcn_bipolar(data)
        % L-bipolar
        dataBipolar(1,:)=data(1,:)-data(5,:);%Fp1-F7
        dataBipolar(2,:)=data(5,:)-data(6,:);%F7-T3
        dataBipolar(3,:)=data(6,:)-data(7,:);%T3-T5
        dataBipolar(4,:)=data(7,:)-data(8,:);%T5-O1
        dataBipolar(5,:)=data(12,:)-data(16,:);%Fp2-F8
        dataBipolar(6,:)=data(16,:)-data(17,:);%F8-T4
        dataBipolar(7,:)=data(17,:)-data(18,:);%T4-T6
        dataBipolar(8,:)=data(18,:)-data(19,:);%T6-O2        
        dataBipolar(9,:)=data(1,:)-data(2,:);%Fp1-F3
        dataBipolar(10,:)=data(2,:)-data(3,:);%F3-C3
        dataBipolar(11,:)=data(3,:)-data(4,:);%C3-P3
        dataBipolar(12,:)=data(4,:)-data(8,:);%P3-O1
        dataBipolar(13,:)=data(12,:)-data(13,:);%Fp2-F4
        dataBipolar(14,:)=data(13,:)-data(14,:);%F4-C4
        dataBipolar(15,:)=data(14,:)-data(15,:);%C4-P4
        dataBipolar(16,:)=data(15,:)-data(19,:);%P4-O2
        dataBipolar(17,:)=data(9,:)-data(10,:);%Fz-Cz
        dataBipolar(18,:)=data(10,:)-data(11,:);%Cz-Pz
    end

    function fcn_plotEEG(ax,seg,segT)
        % Plot 10sec EEG
        mm=size(seg,1);
        set(f,'CurrentAxes',ax);cla(ax)
        hold(ax,'on')
            % Grid dash lines per second 
            for k=1:round((tt(end)-tt(1)+1)/Fs)
                line([tt(1)+Fs*(k-1) tt(1)+Fs*(k-1)],[0 mm+1],'linestyle','--','color',[0 0 0])
            end
            
            % plot EEG
            plot(ax,tt,zScale*seg(1:end-1,:)+DCoff(1:end-1,:),'k');
            
            % plot EKG (z-normalized)
            ekg=seg(end,:);ekg=(ekg-mean(ekg))/(eps+std(ekg));
            plot(ax,tt,.2*ekg+DCoff(end,:),'r');
            
            % show rulers (scales)
            ddt=tt(end)-tt(1)+1;a=round(ddt*4/5);xa1=tt(1)+[a a+Fs-1];ya1=[3 3];xa2=tt(1)+[a a];ya2=ya1+[0 100*zScale];
            text(ax,xa1(1)-Fs/10,mean(ya2),'100\muV','Color','b','FontSize',8,'verticalalignment','middle','horizontalalignment','right');text(ax,mean(xa1),ya1(1)-0.1,'1 sec','Color','b','FontSize',8,'verticalalignment','top','horizontalalignment','center');
            line(ax,xa1,ya1,'LineWidth',2,'Color','b');line(ax,xa2,ya2,'LineWidth',2,'Color','b');
            
            set(ax,'ytick',1:mm,'yticklabel',fliplr(channel_withspace),'box','on','ylim',[0 mm+1],'xlim',[tt(1) tt(end)+1],'xtick',round(tt(1):1*Fs:tt(end)+1),'xticklabel',segT,'fontsize',9.5);
        hold(ax,'off')    
    end

    function fcn_plotSpect(Ax_spec,sdata)
        % Plot 10min 4 regional-average spectrograms (dB scale)
        winSize=10;
        tto=0;tt1=60*winSize;ttc=30*winSize;
        stepSize=2;S_x=tto:stepSize:tt1;S_y=1:20;
        for iReg=1:4
            set(f,'CurrentAxes',Ax_spec{iReg});cla(Ax_spec{iReg})
            spec=sdata{iReg,2};
            hold(Ax_spec{iReg},'on');
                % 2D spectrogram
                imagesc(Ax_spec{iReg},S_x,S_y,pow2db(spec),col);axis(Ax_spec{iReg},'xy');
                % central dash line (aligned in time with 10sec EEG)
                plot([ttc  ttc],[S_y(1) S_y(end)],'k--','linewidth',1);
            hold(Ax_spec{iReg},'off');
            
            % Frequency axis settings
            ylabel(Ax_spec{iReg},'Freq (Hz)');
            yticks=get(Ax_spec{iReg},'ytick');
            yticklabels=get(Ax_spec{iReg},'yticklabel');yticklabels{end}=sdata{iReg,1};
            if iReg<4
                set(Ax_spec{iReg},'ylim',[S_y(1) S_y(end)],'xlim',[tto tt1],'yticklabel',yticklabels,'ytick',yticks,'xtick',[],'box','on')  
            else
                tt_=segTime-seconds(winSize/2*60-5)+seconds(tto:2.5*60:(tt1+1));
                set(Ax_spec{iReg},'ylim',[S_y(1) S_y(end)],'xlim',[tto tt1],'yticklabel',yticklabels,'ytick',yticks,'xtick',tto:2.5*60:(tt1+1),'xticklabel',datestr(tt_,'hh:MM:ss'),'box','on');
            end
        end

        % Marker on the top of spectrogram
        set(f,'CurrentAxes',Ax_spec{end});cla(Ax_spec{end});
        plot(Ax_spec{end},ttc,0,'rv','markersize',10,'MarkerFaceColor','r');
        axis(Ax_spec{end},'off')
        set(Ax_spec{end},'xtick',[],'xlim',get(Ax_spec{end-1},'xlim'),'ylim',[-.7 .5])         
    end
end
