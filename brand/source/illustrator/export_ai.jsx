// WFS Brand Identity 1.0 — batch-convert SVG masters to native Adobe Illustrator (.ai)
// Run from Illustrator: File > Scripts > Other Script... ; select the /brand folder when asked.
#target illustrator
(function () {
    var root = Folder.selectDialog('Select the WFS /brand folder');
    if (!root) return;
    var groups = ['logo', 'icon', 'wordmark'];
    var done = 0, failed = [];
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    for (var g = 0; g < groups.length; g++) {
        var src = new Folder(root.fsName + '/' + groups[g] + '/svg');
        var dst = new Folder(root.fsName + '/' + groups[g] + '/ai');
        if (!src.exists) continue;
        if (!dst.exists) dst.create();
        var files = src.getFiles('*.svg');
        for (var i = 0; i < files.length; i++) {
            try {
                var doc = app.open(files[i]);
                var opts = new IllustratorSaveOptions();
                opts.compatibility = Compatibility.ILLUSTRATOR17;   // CC; PDF-compatible
                opts.pdfCompatible = true;
                opts.embedICCProfile = false;
                opts.compressed = true;
                var name = files[i].name.replace(/\.svg$/i, '.ai');
                doc.saveAs(new File(dst.fsName + '/' + name), opts);
                doc.close(SaveOptions.DONOTSAVECHANGES);
                done++;
            } catch (e) { failed.push(files[i].name + ': ' + e); }
        }
    }
    app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS;
    alert('WFS: saved ' + done + ' native .ai files.' + (failed.length ? '\nFailed:\n' + failed.join('\n') : ''));
})();
